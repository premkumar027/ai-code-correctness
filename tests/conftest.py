"""Test bootstrap.

These tests import from src/, which pulls in src.config -> python-dotenv. The
`pytest` on PATH is a system install that does not have the project's
dependencies, and deliberately so: it is the interpreter that executes all
generated code, and swapping it mid-study would change the evaluation
environment for new runs relative to the 888 already collected.

So instead of installing pytest into the venv (which would win the PATH lookup in
src/evaluation/python_runner.py and silently move generated-code execution from
Python 3.10 to 3.12), stub the one import that is missing. Test-only.
"""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import dotenv  # noqa: F401
except ModuleNotFoundError:
    stub = types.ModuleType("dotenv")
    stub.load_dotenv = lambda *a, **k: False
    sys.modules["dotenv"] = stub
