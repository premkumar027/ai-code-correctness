"""Fast unit tests for the self-tests arm's response parsing.

Parsing is the fragile part of the arm: if the implementation and test blocks are
split wrongly, a good answer is scored as a failure. Run with:

    uv run pytest tests/ -q
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.extract import extract_impl_and_tests
from src.evaluation.python_runner import normalize_test_imports


def _blocks(impl_body, test_body, marked=True):
    impl_head = "# === IMPLEMENTATION ===\n" if marked else ""
    test_head = "# === TESTS ===\n" if marked else ""
    return (
        f"```python\n{impl_head}{impl_body}\n```\n\n"
        f"```python\n{test_head}{test_body}\n```\n"
    )


IMPL = "def f(x):\n    return x + 1"
TESTS = "from solution import f\n\ndef test_f():\n    assert f(1) == 2"


def test_marked_blocks():
    impl, tests = extract_impl_and_tests(_blocks(IMPL, TESTS))
    assert "def f(x)" in impl and "def test_f" not in impl
    assert "def test_f" in tests


def test_unmarked_blocks_fall_back_to_test_detection():
    impl, tests = extract_impl_and_tests(_blocks(IMPL, TESTS, marked=False))
    assert "def f(x)" in impl and "def test_f" not in impl
    assert "def test_f" in tests


def test_single_block_containing_both_markers_is_split():
    response = (
        "```python\n"
        "# === IMPLEMENTATION ===\n"
        f"{IMPL}\n\n"
        "# === TESTS ===\n"
        f"{TESTS}\n"
        "```\n"
    )
    impl, tests = extract_impl_and_tests(response)
    assert "def f(x)" in impl and "def test_f" not in impl
    assert "def test_f" in tests


def test_prose_and_a_complexity_snippet_do_not_confuse_extraction():
    # chain_of_thought responses often trail an unrelated block; the marked
    # blocks must still win over "last block in the response".
    response = (
        "First I explain my approach.\n\n"
        + _blocks(IMPL, TESTS)
        + "\nComplexity:\n\n```\nO(n log n) time, O(n) space\n```\n"
    )
    impl, tests = extract_impl_and_tests(response)
    assert "def f(x)" in impl
    assert "def test_f" in tests


def test_no_code_at_all_returns_none():
    assert extract_impl_and_tests("I cannot help with that.") == (None, None)


def test_only_tests_returns_none_for_impl():
    impl, tests = extract_impl_and_tests(f"```python\n# === TESTS ===\n{TESTS}\n```")
    assert impl is None
    assert "def test_f" in tests


def test_import_normalization_rewrites_stray_module_names():
    assert "from solution import f" in normalize_test_imports("from reference import f")
    assert "from solution import f" in normalize_test_imports("from implementation import f")
    assert "import solution as ref" in normalize_test_imports("import reference as ref")
    assert "import solution as reference" in normalize_test_imports("import reference")


def test_import_normalization_leaves_real_imports_alone():
    src = "import pytest\nfrom solution import f\nfrom collections import deque"
    assert normalize_test_imports(src) == src
