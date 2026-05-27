"""
Batch experiment runner: loops all models × tasks × prompt styles,
retries failures up to 5 times with test feedback, logs everything to SQLite.

Usage:
    uv run python src/orchestrator.py
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
from src.evaluation.python_runner import run as run_tests
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
    skipped: bool = False       # dry-run
    api_error: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_code(response: str) -> str:
    """Return the last Python code block, or the raw response if none found."""
    blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
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
        result = run_tests(last_code, task_name)

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
# Summary
# ---------------------------------------------------------------------------

def _print_summary(results: list[ComboResult]) -> None:
    passed = [r for r in results if r.passed]
    total  = [r for r in results if not r.skipped]

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

    print("=" * 68)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Run LLM code-generation experiments across models × tasks × prompt styles."
    )
    parser.add_argument(
        "--model", action="append", dest="models", metavar="NAME",
        help=f"Model to include (repeat for multiple). Choices: {', '.join(get_model_names())}",
    )
    parser.add_argument(
        "--task", action="append", dest="tasks", metavar="NAME",
        help=f"Task to include (repeat for multiple). Choices: {', '.join(TASKS.keys())}",
    )
    parser.add_argument(
        "--prompt-style", action="append", dest="styles", metavar="STYLE",
        help="Prompt style to include (repeat for multiple). Choices: naive, structured, chain_of_thought",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would run without making any API calls.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    models = args.models or get_model_names()
    tasks  = args.tasks  or list(TASKS.keys())
    styles = args.styles or ["naive", "structured", "chain_of_thought"]

    # validate
    bad_models = [m for m in models if m not in MODEL_CONFIGS]
    bad_tasks  = [t for t in tasks  if t not in TASKS]
    bad_styles = [s for s in styles if s not in ("naive", "structured", "chain_of_thought")]
    if bad_models:
        sys.exit(f"Unknown model(s): {bad_models}. Valid: {get_model_names()}")
    if bad_tasks:
        sys.exit(f"Unknown task(s): {bad_tasks}. Valid: {list(TASKS.keys())}")
    if bad_styles:
        sys.exit(f"Unknown style(s): {bad_styles}. Valid: naive, structured, chain_of_thought")

    total_combos = len(models) * len(tasks) * len(styles)
    mode = "DRY RUN — no API calls" if args.dry_run else "LIVE"
    print(f"[{mode}] {total_combos} combos "
          f"({len(models)} models × {len(tasks)} tasks × {len(styles)} styles)")
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
                result = run_combo(model_name, task_name, style, dry_run=args.dry_run)
                all_results.append(result)

    if not args.dry_run:
        _print_summary(all_results)


if __name__ == "__main__":
    main()
