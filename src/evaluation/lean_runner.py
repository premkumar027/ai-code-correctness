"""
Lean 4 evaluation runner: writes generated code to the appropriate Lake workspace,
runs `lake build`, parses compiler errors, and counts `sorry` occurrences.

Library options
  "none"    – lean_workspace/no_lib/   (no external deps, ~5s build)
  "mathlib" – lean_workspace/mathlib/  (one-time setup: lake update && lake exe cache get)
  "cslib"   – lean_workspace/cslib/    (one-time setup: lake update, fill in URL in lakefile.lean)

NOTE: each workspace has a single LLMSolution.lean that is overwritten per run.
Concurrent runs against the same library will conflict — run the orchestrator
sequentially (the default) to avoid this.
"""

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LEAN_WORKSPACE = PROJECT_ROOT / "lean_workspace"
SOLUTION_FILE = "LLMSolution.lean"

_ELAN_BIN = Path.home() / ".elan" / "bin"
_LEAN_ENV = {**os.environ, "PATH": str(_ELAN_BIN) + ":" + os.environ.get("PATH", "")}

_WORKSPACE_DIR = {
    "none": "no_lib",
    "mathlib": "mathlib",
    "cslib": "cslib",
}

_TIMEOUTS = {
    "none": 120,
    "mathlib": 300,
    "cslib": 300,
}


@dataclass
class LeanRunResult:
    compiled: bool
    sorry_count: int
    error_message: str
    uses_mathlib: bool

    @property
    def passed(self) -> bool:
        """True only when the code compiled cleanly with zero sorry."""
        return self.compiled and self.sorry_count == 0


def run(code: str, task_name: str, library: str = "none") -> LeanRunResult:
    """
    Write `code` to LLMSolution.lean in the selected workspace and run lake build.
    `task_name` is accepted for API consistency with python_runner but not used here.
    """
    if library not in _TIMEOUTS:
        raise ValueError(f"Unknown lean_library {library!r}. Choose: {list(_TIMEOUTS)}")

    workspace = LEAN_WORKSPACE / _WORKSPACE_DIR[library]
    solution_path = workspace / SOLUTION_FILE

    sorry_count = len(re.findall(r"\bsorry\b", code))
    uses_mathlib = (
        library == "mathlib"
        or bool(re.search(r"^\s*import\s+Mathlib", code, re.MULTILINE))
    )

    solution_path.write_text(code, encoding="utf-8")

    timeout = _TIMEOUTS[library]
    try:
        proc = subprocess.run(
            ["lake", "build", "LLMSolution"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_LEAN_ENV,
        )
    except subprocess.TimeoutExpired:
        return LeanRunResult(
            compiled=False,
            sorry_count=sorry_count,
            error_message=(
                f"lake build timed out after {timeout}s. "
                f"If using '{library}', ensure `lake exe cache get` has been run."
            ),
            uses_mathlib=uses_mathlib,
        )
    except FileNotFoundError:
        return LeanRunResult(
            compiled=False,
            sorry_count=sorry_count,
            error_message="lake not found. Make sure elan/lake is installed (~/.elan/bin).",
            uses_mathlib=uses_mathlib,
        )

    output = proc.stdout + proc.stderr
    compiled = proc.returncode == 0

    if compiled and sorry_count > 0:
        error_message = (
            f"Code compiled, but contains {sorry_count} sorry placeholder(s). "
            "sorry bypasses proof obligations and is not allowed. "
            "Please remove all sorry and provide complete proofs."
        )
    elif compiled:
        error_message = "Compiled successfully with no sorry."
    else:
        error_message = _extract_errors(output, str(workspace))

    return LeanRunResult(
        compiled=compiled,
        sorry_count=sorry_count,
        error_message=error_message,
        uses_mathlib=uses_mathlib,
    )


def _extract_errors(output: str, workspace_path: str) -> str:
    """Return cleaned compiler errors with absolute workspace paths stripped."""
    lines = output.splitlines()
    relevant = []
    for line in lines:
        # Skip lake progress/trace lines and blank lines (✔ = ✔, ✖ = ✖)
        if re.match(r"^\s*(✔|✖|Building |Compiling |info: |trace: |\s*$)", line):
            continue
        # Shorten absolute paths so feedback is readable
        line = line.replace(workspace_path + "/", "")
        line = line.replace(workspace_path, "")
        relevant.append(line)

    cleaned = "\n".join(relevant).strip()
    if not cleaned:
        cleaned = output.strip()

    return cleaned[:4000] if len(cleaned) > 4000 else cleaned
