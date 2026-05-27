import pytest


def test_is_prefix_closed_true(is_prefix_closed):
    assert is_prefix_closed({"", "a", "ab", "abc"}) is True


def test_is_prefix_closed_false(is_prefix_closed):
    # "ab" is in S but "a" is not
    assert is_prefix_closed({"", "ab", "abc"}) is False


def test_empty_set_is_prefix_closed(is_prefix_closed):
    assert is_prefix_closed(set()) is True


def test_only_empty_string(is_prefix_closed):
    assert is_prefix_closed({""}) is True


def test_single_char_with_empty(is_prefix_closed):
    assert is_prefix_closed({"", "a"}) is True


def test_single_char_without_empty(is_prefix_closed):
    assert is_prefix_closed({"a"}) is False


def test_closure_contains_all_prefixes(prefix_closure):
    result = prefix_closure({"abc"})
    assert result == {"", "a", "ab", "abc"}


def test_closure_of_empty_set(prefix_closure):
    assert prefix_closure(set()) == set()


def test_closure_already_closed(prefix_closure):
    S = {"", "a", "ab"}
    assert prefix_closure(S) == S


def test_closure_is_prefix_closed(is_prefix_closed, prefix_closure):
    S = {"abc", "xy", "xyz"}
    assert is_prefix_closed(prefix_closure(S)) is True


def test_closure_is_smallest(prefix_closure):
    result = prefix_closure({"ab", "cd"})
    assert result == {"", "a", "ab", "c", "cd"}


def test_closure_idempotent(prefix_closure):
    S = {"hello", "world"}
    assert prefix_closure(prefix_closure(S)) == prefix_closure(S)
