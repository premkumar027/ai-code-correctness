import pytest


def test_basic_word(prefix_suffix_split):
    result = prefix_suffix_split("abc")
    assert ("", "abc") in result
    assert ("a", "bc") in result
    assert ("ab", "c") in result
    assert ("abc", "") in result


def test_length_is_n_plus_one(prefix_suffix_split):
    assert len(prefix_suffix_split("hello")) == 6


def test_empty_string(prefix_suffix_split):
    result = prefix_suffix_split("")
    assert result == [("", "")]


def test_single_char(prefix_suffix_split):
    result = prefix_suffix_split("x")
    assert ("", "x") in result
    assert ("x", "") in result
    assert len(result) == 2


def test_concat_invariant(prefix_suffix_split):
    word = "python"
    for p, s in prefix_suffix_split(word):
        assert p + s == word


def test_all_prefixes_covered(prefix_suffix_split):
    word = "test"
    prefixes = [p for p, _ in prefix_suffix_split(word)]
    assert prefixes == ["", "t", "te", "tes", "test"]


def test_all_suffixes_covered(prefix_suffix_split):
    word = "test"
    suffixes = [s for _, s in prefix_suffix_split(word)]
    assert suffixes == ["test", "est", "st", "t", ""]


def test_no_duplicates(prefix_suffix_split):
    result = prefix_suffix_split("aaa")
    assert len(result) == len(set(result))


def test_long_word(prefix_suffix_split):
    word = "a" * 100
    result = prefix_suffix_split(word)
    assert len(result) == 101
    for p, s in result:
        assert p + s == word
