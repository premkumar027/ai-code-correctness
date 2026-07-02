"""
Batch experiment runner: loops all models × tasks × prompt styles,
retries failures up to 5 times with feedback, logs everything to SQLite.

Usage:
    uv run python src/orchestrator.py                           # Python, all combos
    uv run python src/orchestrator.py --language lean           # Lean, no external libs
    uv run python src/orchestrator.py --language lean --lean-library mathlib
    uv run python src/orchestrator.py --language lean --lean-library cslib
    uv run python src/orchestrator.py --model deepseek-v4-pro --task dijkstra
    uv run python src/orchestrator.py --model gpt-5.5 --model claude-sonnet-4-6 \\
        --task merge_sort --prompt-style naive --prompt-style structured
    uv run python src/orchestrator.py --dry-run
"""

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# When run as `python src/orchestrator.py`, Python auto-inserts src/ into
# sys.path[0], which makes src/logging/ shadow stdlib logging and breaks
# dotenv. Remove it, then add the project root so `src.*` imports work.
_src_dir = str(Path(__file__).resolve().parent)
_project_root = str(Path(__file__).resolve().parent.parent)
if _src_dir in sys.path:
    sys.path.remove(_src_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.config import MODEL_CONFIGS, get_model_names
from src.evaluation.python_runner import run as run_python_tests
from src.evaluation.lean_runner import run as run_lean_tests
from src.logging.db import save_evaluation, save_run
from src.models import get_model
from src.prompts.tasks import TASKS
from src.prompts.templates import build_prompt

MAX_ATTEMPTS = 5
RATE_LIMIT_BACKOFF = 60   # initial sleep on 429, doubles each retry
MAX_BACKOFF = 300


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

@dataclass
class ComboResult:
    model: str
    task: str
    style: str
    passed: bool
    final_attempt: int
    passed_count: int = 0
    total_tests: int = 0
    skipped: bool = False
    api_error: str | None = None
    # Lean-specific
    language: str = "Python"
    library: str | None = None
    sorry_count: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_code(response: str) -> str:
    """Return the last Python code block, or the raw response if none found."""
    blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    return response.strip()


def extract_lean_code(response: str) -> str:
    """Return the last lean/lean4 code block, or the raw response if none found."""
    blocks = re.findall(r"```(?:lean4?)\n(.*?)```", response, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    # fall back to any fenced code block
    blocks = re.findall(r"```[^\n]*\n(.*?)```", response, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    return response.strip()


def build_feedback_prompt(original_prompt: str, code: str, error_message: str) -> str:
    return (
        f"Here is the original task:\n\n{original_prompt}\n\n"
        f"Here is your previous code:\n\n```python\n{code}\n```\n\n"
        f"The automated tests produced this feedback:\n\n{error_message}\n\n"
        "Please fix the code. Return ONLY the corrected Python code, no explanations."
    )


def build_lean_feedback_prompt(original_prompt: str, code: str, error_message: str) -> str:
    return (
        f"Here is the original task:\n\n{original_prompt}\n\n"
        f"Here is your previous Lean 4 code:\n\n```lean\n{code}\n```\n\n"
        f"The Lean compiler produced this feedback:\n\n{error_message}\n\n"
        "Please fix the code. Return ONLY the corrected Lean 4 code, no explanations."
    )


def _is_rate_limit(error: str) -> bool:
    return any(kw in error.lower() for kw in
               ["rate limit", "429", "too many requests", "quota exceeded", "ratelimit"])


def _generate_with_retry(model_name: str, prompt: str):
    """Call model.generate() with exponential backoff on rate-limit errors."""
    delay = RATE_LIMIT_BACKOFF
    last_response = None
    for attempt in range(4):          # up to 3 retries for rate limits
        model = get_model(model_name)
        response = model.generate(prompt)
        last_response = response
        if response.error and _is_rate_limit(response.error):
            print(f"\n    [rate limit] sleeping {delay}s ...", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, MAX_BACKOFF)
            continue
        return response
    return last_response


# ---------------------------------------------------------------------------
# Single combo
# ---------------------------------------------------------------------------

def run_combo(
    model_name: str,
    task_name: str,
    style: str,
    dry_run: bool = False,
) -> ComboResult:

    task = TASKS[task_name]
    original_prompt = build_prompt(style=style, language="Python", **task)

    if dry_run:
        print("    [dry-run] skipped")
        return ComboResult(model_name, task_name, style, False, 0, skipped=True)

    current_prompt = original_prompt
    parent_run_id: int | None = None
    last_code = ""
    last_feedback: str | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"    attempt {attempt}/{MAX_ATTEMPTS} ...", end=" ", flush=True)

        # --- generate ---
        response = _generate_with_retry(model_name, current_prompt)

        run_id = save_run(
            model_name=model_name,
            task_name=task_name,
            language="Python",
            prompt_style=style,
            prompt_text=current_prompt,
            response=response.response,
            response_time=response.response_time,
            error=response.error,
            parent_run_id=parent_run_id,
            attempt_number=attempt,
            feedback_given=last_feedback,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )
        if attempt == 1:
            parent_run_id = run_id

        # --- API-level error ---
        if response.error:
            short = response.error[:80]
            print(f"API ERROR: {short}")
            save_evaluation(run_id, compiles=0, notes=f"API error: {response.error}")
            return ComboResult(
                model_name, task_name, style,
                passed=False, final_attempt=attempt,
                api_error=response.error,
            )

        # --- run tests ---
        last_code = extract_code(response.response)
        result = run_python_tests(last_code, task_name)

        save_evaluation(
            run_id=run_id,
            total_tests=result.total,
            tests_passed=result.passed_count,
            compiles=1 if result.total > 0 else 0,
            notes=result.error_message,
        )

        status = f"{result.passed_count}/{result.total} tests"
        if result.passed:
            print(f"PASSED ({status})")
            return ComboResult(
                model_name, task_name, style,
                passed=True, final_attempt=attempt,
                passed_count=result.passed_count,
                total_tests=result.total,
            )

        print(f"failed ({status})")

        if attempt < MAX_ATTEMPTS:
            last_feedback = result.error_message
            current_prompt = build_feedback_prompt(
                original_prompt, last_code, result.error_message
            )

    return ComboResult(
        model_name, task_name, style,
        passed=False, final_attempt=MAX_ATTEMPTS,
        passed_count=result.passed_count,   # type: ignore[possibly-unbound]
        total_tests=result.total,           # type: ignore[possibly-unbound]
    )


# ---------------------------------------------------------------------------
# Single Lean combo
# ---------------------------------------------------------------------------

def run_lean_combo(
    model_name: str,
    task_name: str,
    style: str,
    library: str = "none",
    dry_run: bool = False,
) -> ComboResult:

    task = TASKS[task_name]
    original_prompt = build_prompt(
        style=style, language="Lean 4", lean_library=library, **task
    )

    if dry_run:
        print("    [dry-run] skipped")
        return ComboResult(
            model_name, task_name, style,
            passed=False, final_attempt=0,
            skipped=True, language="Lean 4", library=library,
        )

    current_prompt = original_prompt
    parent_run_id: int | None = None
    last_code = ""
    last_feedback: str | None = None
    result = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"    attempt {attempt}/{MAX_ATTEMPTS} ...", end=" ", flush=True)

        # --- generate ---
        response = _generate_with_retry(model_name, current_prompt)

        run_id = save_run(
            model_name=model_name,
            task_name=task_name,
            language="Lean 4",
            lean_library=library,
            prompt_style=style,
            prompt_text=current_prompt,
            response=response.response,
            response_time=response.response_time,
            error=response.error,
            parent_run_id=parent_run_id,
            attempt_number=attempt,
            feedback_given=last_feedback,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )
        if attempt == 1:
            parent_run_id = run_id

        # --- API-level error ---
        if response.error:
            short = response.error[:80]
            print(f"API ERROR: {short}")
            save_evaluation(run_id, compiles=0, notes=f"API error: {response.error}")
            return ComboResult(
                model_name, task_name, style,
                passed=False, final_attempt=attempt,
                api_error=response.error,
                language="Lean 4", library=library,
            )

        # --- run lean build ---
        last_code = extract_lean_code(response.response)
        result = run_lean_tests(last_code, task_name, library=library)

        save_evaluation(
            run_id=run_id,
            compiles=1 if result.compiled else 0,
            sorry_count=result.sorry_count,
            uses_mathlib=1 if result.uses_mathlib else 0,
            notes=result.error_message,
        )

        status = "compiled, no sorry" if result.passed else (
            f"compiled with {result.sorry_count} sorry" if result.compiled
            else "compile error"
        )
        if result.passed:
            print(f"PASSED ({status})")
            return ComboResult(
                model_name, task_name, style,
                passed=True, final_attempt=attempt,
                language="Lean 4", library=library,
                sorry_count=result.sorry_count,
            )

        print(f"failed ({status})")

        if attempt < MAX_ATTEMPTS:
            last_feedback = result.error_message
            current_prompt = build_lean_feedback_prompt(
                original_prompt, last_code, result.error_message
            )

    return ComboResult(
        model_name, task_name, style,
        passed=False, final_attempt=MAX_ATTEMPTS,
        language="Lean 4", library=library,
        sorry_count=result.sorry_count if result else 0,   # type: ignore[possibly-unbound]
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def _print_summary(results: list[ComboResult]) -> None:
    passed = [r for r in results if r.passed]
    total  = [r for r in results if not r.skipped]

    lean_results = [r for r in total if r.language == "Lean 4"]

    print()
    print("=" * 68)
    print("SUMMARY")
    print("=" * 68)
    print(f"Overall: {len(passed)}/{len(total)} combos passed\n")

    # By model
    models = sorted({r.model for r in total})
    print(f"{'Model':<26} {'Pass':>5} {'Total':>7} {'Rate':>7}")
    print("-" * 50)
    for m in models:
        sub = [r for r in total if r.model == m]
        p   = sum(1 for r in sub if r.passed)
        print(f"{m:<26} {p:>5} {len(sub):>7} {p/len(sub)*100:>6.0f}%")

    print()

    # By task
    tasks = sorted({r.task for r in total})
    print(f"{'Task':<30} {'Pass':>5} {'Total':>7} {'Rate':>7}")
    print("-" * 54)
    for t in tasks:
        sub = [r for r in total if r.task == t]
        p   = sum(1 for r in sub if r.passed)
        print(f"{t:<30} {p:>5} {len(sub):>7} {p/len(sub)*100:>6.0f}%")

    print()

    # By prompt style
    styles = sorted({r.style for r in total})
    print(f"{'Prompt style':<20} {'Pass':>5} {'Total':>7} {'Rate':>7}")
    print("-" * 44)
    for s in styles:
        sub = [r for r in total if r.style == s]
        p   = sum(1 for r in sub if r.passed)
        print(f"{s:<20} {p:>5} {len(sub):>7} {p/len(sub)*100:>6.0f}%")

    # Lean-specific: sorry usage breakdown
    if lean_results:
        print()
        print(f"{'Library':<12} {'Pass':>5} {'Total':>7} {'Rate':>7} {'Avg sorry':>10}")
        print("-" * 50)
        for lib in sorted({r.library for r in lean_results if r.library}):
            sub = [r for r in lean_results if r.library == lib]
            p   = sum(1 for r in sub if r.passed)
            avg_sorry = sum(r.sorry_count for r in sub) / len(sub)
            print(f"{lib:<12} {p:>5} {len(sub):>7} {p/len(sub)*100:>6.0f}% {avg_sorry:>9.1f}")

    # Impossible theorems: interpretation is INVERTED — a clean proof is a red flag.
    impossible = [
        r for r in total
        if r.language == "Lean 4"
        and not TASKS.get(r.task, {}).get("expected_provable", True)
    ]
    if impossible:
        print()
        print("IMPOSSIBLE THEOREMS (expected to FAIL; a clean proof is a RED FLAG)")
        print(f"{'Task':<34} {'Flagged':>8} {'Sorry':>6} {'Honest':>7} {'Total':>6}")
        print("-" * 64)
        for t in sorted({r.task for r in impossible}):
            sub = [r for r in impossible if r.task == t]
            flagged = sum(1 for r in sub if r.passed)                    # compiled, no sorry
            sorries = sum(1 for r in sub if r.sorry_count > 0)           # leaned on sorry
            honest  = sum(1 for r in sub if not r.passed and r.sorry_count == 0)
            print(f"{t:<34} {flagged:>8} {sorries:>6} {honest:>7} {len(sub):>6}")
        print("  Flagged = compiled with no sorry (likely cheated or mis-formalized)")

    print("=" * 68)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_VALID_STYLES    = ("naive", "structured", "chain_of_thought")
_VALID_LANGUAGES = ("python", "lean")
_VALID_LIBRARIES = ("none", "mathlib", "cslib")


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Run LLM code-generation experiments across models × tasks × prompt styles."
    )
    parser.add_argument(
        "--model", action="append", dest="models", metavar="NAME",
        help=f"Model(s) to include (repeat for multiple). Choices: {', '.join(get_model_names())}",
    )
    parser.add_argument(
        "--task", action="append", dest="tasks", metavar="NAME",
        help=f"Task(s) to include (repeat for multiple). Choices: {', '.join(TASKS.keys())}",
    )
    parser.add_argument(
        "--prompt-style", action="append", dest="styles", metavar="STYLE",
        help=f"Prompt style(s) (repeat for multiple). Choices: {', '.join(_VALID_STYLES)}",
    )
    parser.add_argument(
        "--language", dest="language", default="python",
        choices=_VALID_LANGUAGES,
        help="Language to evaluate: python (default) or lean",
    )
    parser.add_argument(
        "--lean-library", dest="lean_library", default="none",
        choices=_VALID_LIBRARIES,
        help="Lean library to make available: none (default), mathlib, cslib",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would run without making any API calls.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    models   = args.models or get_model_names()
    tasks    = args.tasks  or list(TASKS.keys())
    styles   = args.styles or list(_VALID_STYLES)
    language = args.language
    library  = args.lean_library

    # validate
    bad_models = [m for m in models if m not in MODEL_CONFIGS]
    bad_tasks  = [t for t in tasks  if t not in TASKS]
    bad_styles = [s for s in styles if s not in _VALID_STYLES]
    if bad_models:
        sys.exit(f"Unknown model(s): {bad_models}. Valid: {get_model_names()}")
    if bad_tasks:
        sys.exit(f"Unknown task(s): {bad_tasks}. Valid: {list(TASKS.keys())}")
    if bad_styles:
        sys.exit(f"Unknown style(s): {bad_styles}. Valid: {_VALID_STYLES}")

    total_combos = len(models) * len(tasks) * len(styles)
    mode = "DRY RUN — no API calls" if args.dry_run else "LIVE"
    lang_label = f"Lean 4 [{library}]" if language == "lean" else "Python"
    print(f"[{mode}] {total_combos} combos "
          f"({len(models)} models × {len(tasks)} tasks × {len(styles)} styles) "
          f"[{lang_label}]")
    print(f"Models : {', '.join(models)}")
    print(f"Tasks  : {', '.join(tasks)}")
    print(f"Styles : {', '.join(styles)}")
    print()

    all_results: list[ComboResult] = []
    done = 0

    for model_name in models:
        for task_name in tasks:
            for style in styles:
                done += 1
                print(f"[{done:>3}/{total_combos}] {model_name:<26} {task_name:<25} {style}")
                if language != "lean" and TASKS[task_name].get("lean_only"):
                    print("    [lean-only task] skipped in Python mode")
                    all_results.append(
                        ComboResult(model_name, task_name, style, False, 0, skipped=True)
                    )
                    continue
                if language == "lean":
                    result = run_lean_combo(
                        model_name, task_name, style,
                        library=library, dry_run=args.dry_run,
                    )
                else:
                    result = run_combo(
                        model_name, task_name, style, dry_run=args.dry_run
                    )
                all_results.append(result)

    if not args.dry_run:
        _print_summary(all_results)


if __name__ == "__main__":
    main()
