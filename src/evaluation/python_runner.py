import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TASKS_DIR = PROJECT_ROOT / "tasks"
TIMEOUT = 120

# pytest may live outside the project venv (e.g. system Python install).
# Kept as a list so the fallback form doesn't become one argv element with spaces.
_pytest_bin = shutil.which("pytest")
_PYTEST_CMD = [_pytest_bin] if _pytest_bin else [sys.executable, "-m", "pytest"]

_PYTEST_FLAGS = ["--tb=short", "-v", "--no-header", "-p", "no:cacheprovider"]


@dataclass
class PythonRunResult:
    passed: bool
    total: int
    passed_count: int
    failed_count: int
    error_message: str


def run(code: str, task_name: str, timeout: int = TIMEOUT) -> PythonRunResult:
    """Run the task's hidden human test suite against `code`."""
    task_dir = TASKS_DIR / task_name
    test_files = list(task_dir.glob("test_*.py"))
    conftest = task_dir / "conftest.py"

    if not test_files:
        return PythonRunResult(False, 0, 0, 0, f"No test file found for task '{task_name}'.")
    if not conftest.exists():
        return PythonRunResult(False, 0, 0, 0, f"No conftest.py found for task '{task_name}'.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "reference.py").write_text(code, encoding="utf-8")
        shutil.copy(conftest, tmp_path / "conftest.py")
        shutil.copy(test_files[0], tmp_path / test_files[0].name)

        return _pytest(tmp_path, timeout=timeout, cwd=PROJECT_ROOT)


def run_pair(impl_code: str, test_code: str, timeout: int = TIMEOUT) -> PythonRunResult:
    """Run a model-authored test suite against an implementation.

    The implementation is written as `solution.py` and the tests as
    `test_generated.py`, matching the import contract stated in the prompt
    (`from solution import ...`). Because the two are decoupled, the same test
    suite can be re-run against the reference implementation or a mutant of it,
    which is how test *strength* is measured.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "solution.py").write_text(impl_code, encoding="utf-8")
        (tmp_path / "test_generated.py").write_text(
            normalize_test_imports(test_code), encoding="utf-8"
        )
        # cwd inside the temp dir so `import solution` resolves to the file above
        # and never to anything in the project tree.
        return _pytest(tmp_path, timeout=timeout, cwd=tmp_path)


def normalize_test_imports(test_code: str) -> str:
    """Point stray imports at `solution`.

    Models occasionally import the implementation as `reference`, `main`,
    `implementation` or the task name. Rewriting these costs nothing and avoids
    scoring a collection error as a test-quality failure.
    """
    aliases = ("reference", "implementation", "impl", "main", "my_solution", "code")
    for alias in aliases:
        test_code = re.sub(rf"^(\s*)from {alias} import\b", r"\1from solution import",
                           test_code, flags=re.MULTILINE)
        test_code = re.sub(rf"^(\s*)import {alias}\s*$", r"\1import solution as " + alias,
                           test_code, flags=re.MULTILINE)
        test_code = re.sub(rf"^(\s*)import {alias} as (\w+)", r"\1import solution as \2",
                           test_code, flags=re.MULTILINE)
    return test_code


def _pytest(target: Path, timeout: int, cwd: Path) -> PythonRunResult:
    env = {**os.environ, "PYTHONPATH": str(target), "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        result = subprocess.run(
            [*_PYTEST_CMD, str(target), *_PYTEST_FLAGS],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
            env=env,
        )
    except subprocess.TimeoutExpired:
        return PythonRunResult(
            False, 0, 0, 0,
            f"Execution timed out after {timeout} seconds. "
            "Check for infinite loops or blocking calls.",
        )

    return _parse_result(result.stdout + result.stderr, result.returncode)


def _parse_result(output: str, returncode: int) -> PythonRunResult:
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    error_match = re.search(r"(\d+) error", output)

    passed_count = int(passed_match.group(1)) if passed_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0
    collection_errors = int(error_match.group(1)) if error_match else 0

    total = passed_count + failed_count

    # Collection-level failure (syntax error, import error, conftest crash).
    # Covers pytest exit codes 2 (interrupted), 3 (internal error), 4 (usage/conftest crash).
    # Also catches explicit ERROR counts in the summary line.
    is_collection_error = (
        collection_errors > 0
        or returncode in (2, 3, 4)
        or "ImportError while loading conftest" in output
        or ("ERROR collecting" in output and total == 0)
    )
    if total == 0 and is_collection_error:
        error_section = _extract_section(output, ("ERRORS", "ERROR"), end_marker="=====")
        if not error_section:
            error_section = output[:3000]
        return PythonRunResult(
            False, 0, 0, 0,
            f"Your code could not be loaded by the test runner:\n\n{error_section.strip()}",
        )

    # Unknown failure (no summary line at all)
    if total == 0 and passed_count == 0 and failed_count == 0:
        snippet = output[-2000:] if len(output) > 2000 else output
        return PythonRunResult(
            False, 0, 0, 0,
            f"pytest exited with code {returncode}. Output:\n{snippet.strip()}",
        )

    all_passed = failed_count == 0 and total > 0

    if all_passed:
        message = f"All {total} tests passed."
    else:
        failure_section = _extract_section(output, ("FAILURES", "ERRORS"), end_marker="=====")
        if failure_section:
            failure_section = failure_section.strip()[:3000]
        else:
            failure_section = "(no detail available)"
        message = (
            f"{passed_count}/{total} tests passed.\n\n"
            f"Failed tests:\n{failure_section}"
        )

    return PythonRunResult(
        passed=all_passed,
        total=total,
        passed_count=passed_count,
        failed_count=failed_count,
        error_message=message,
    )


def _extract_section(output: str, start_markers: tuple, end_marker: str) -> str:
    """Return the text between the first matching start marker and the next end_marker line."""
    lines = output.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if any(marker in line for marker in start_markers):
            start_idx = i
            break
    if start_idx is None:
        return ""
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if end_marker in lines[i] and lines[i].startswith("="):
            end_idx = i
            break
    return "\n".join(lines[start_idx:end_idx])
