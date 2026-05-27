import pytest


def test_is_suffix_closed_true(is_suffix_closed):
    assert is_suffix_closed({"", "c", "bc", "abc"}) is True


def test_is_suffix_closed_false(is_suffix_closed):
    # "bc" is in E but "c" is not
    assert is_suffix_closed({"", "bc", "abc"}) is False


def test_empty_set_is_suffix_closed(is_suffix_closed):
    assert is_suffix_closed(set()) is True


def test_only_empty_string(is_suffix_closed):
    assert is_suffix_closed({""}) is True


def test_single_char_with_empty(is_suffix_closed):
    assert is_suffix_closed({"", "a"}) is True


def test_single_char_without_empty(is_suffix_closed):
    assert is_suffix_closed({"a"}) is False


def test_closure_contains_all_suffixes(suffix_closure):
    result = suffix_closure({"abc"})
    assert result == {"", "c", "bc", "abc"}


def test_closure_of_empty_set(suffix_closure):
    assert suffix_closure(set()) == set()


def test_closure_already_closed(suffix_closure):
    E = {"", "c", "bc"}
    assert suffix_closure(E) == E


def test_closure_is_suffix_closed(is_suffix_closed, suffix_closure):
    E = {"abc", "xy", "xyz"}
    assert is_suffix_closed(suffix_closure(E)) is True


def test_closure_is_smallest(suffix_closure):
    result = suffix_closure({"ab", "cd"})
    assert result == {"", "b", "ab", "d", "cd"}


def test_closure_idempotent(suffix_closure):
    E = {"hello", "world"}
    assert suffix_closure(suffix_closure(E)) == suffix_closure(E)
