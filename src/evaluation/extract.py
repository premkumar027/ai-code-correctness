"""Pulling code out of a model response.

Kept free of API-client and config imports so it can be tested without any
provider SDKs installed — the parsers are the part most likely to silently
misscore a good answer, so they need cheap tests.
"""

import re

IMPL_MARK = "=== IMPLEMENTATION ==="
TEST_MARK = "=== TESTS ==="


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


def extract_impl_and_tests(response: str) -> tuple[str | None, str | None]:
    """Split a self-tests response into (implementation, tests).

    Prefers the marker comments requested in the prompt, and falls back to
    "the block defining test_ functions is the test block" when a model drops
    them. Returns None for whichever part could not be found, so the caller can
    ask for the format again instead of scoring a parse failure as a defect.
    """
    blocks = [
        b.strip()
        for b in re.findall(r"```(?:python)?\s*\n(.*?)```", response, re.DOTALL)
        if b.strip()
    ]
    if not blocks:
        return None, None

    # Everything crammed into one block: split at the tests marker.
    for block in blocks:
        if IMPL_MARK in block and TEST_MARK in block:
            head, _, tail = block.partition(TEST_MARK)
            return head.replace(IMPL_MARK, "").strip(), tail.strip()

    marked_impl = [b for b in blocks if IMPL_MARK in b]
    marked_tests = [b for b in blocks if TEST_MARK in b]
    impl = marked_impl[-1] if marked_impl else None
    tests = marked_tests[-1] if marked_tests else None

    if impl is None or tests is None:
        looks_like_tests = [b for b in blocks if re.search(r"^\s*def test_", b, re.M)]
        if tests is None and looks_like_tests:
            tests = looks_like_tests[-1]
        if impl is None:
            rest = [b for b in blocks if b not in looks_like_tests]
            impl = rest[-1] if rest else None

    return impl, tests
