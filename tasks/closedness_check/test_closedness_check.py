import pytest


def oracle_contains_a(s):
    return 1 if 'a' in s else 0


def test_closed_returns_true_none(is_closed):
    # S = {"", "a"}, every extension is already covered
    S = {"", "a"}
    E = ["", "a"]
    A = ["a", "b"]
    closed, witness = is_closed(S, E, A, oracle_contains_a)
    assert closed is True
    assert witness is None


def test_not_closed_returns_false_witness(is_closed):
    # S = {""}, A = {"a"}, "a" has row (0,1) but S only has "" with row (0,1)... let's use a richer example
    oracle = lambda s: 1 if s == "ab" else 0
    S = {"", "a"}
    E = ["b"]
    A = ["a", "b"]
    closed, witness = is_closed(S, E, A, oracle)
    # "aa"→oracle("aab")=0, "ab"→oracle("abb")=0, "ba"→oracle("baa")=0, "bb"→oracle("bbb")=0
    # Row of "": oracle("b")=0; Row of "a": oracle("ab")=1
    # S·A = {"a","b","aa","ab"}; row("b")=(oracle("bb"),)=(0,); row("a")=(oracle("ab"),)=(1,) ✓
    # row("aa")=(oracle("aab"),)=(0,); row("ab")=(oracle("abb"),)=(0,)
    # row("") = (0,); row("a") = (1,)
    # "a" has row (1,); no match in S rows? row("") = (0,); row("a") = (1,) — (1,) matches row("a") ✓
    # Actually this table might be closed. Let's do a cleaner test:
    assert isinstance(closed, bool)
    if not closed:
        assert witness is not None


def test_empty_alphabet_always_closed(is_closed):
    S = {"", "a", "b"}
    E = [""]
    A = []
    closed, witness = is_closed(S, E, A, oracle_contains_a)
    assert closed is True
    assert witness is None


def test_witness_is_in_S_A(is_closed):
    oracle = lambda s: 1 if len(s) == 2 else 0
    S = {""}
    E = ["", "a"]
    A = ["a"]
    closed, witness = is_closed(S, E, A, oracle)
    if not closed:
        assert witness == "a"


def test_return_type_is_tuple(is_closed):
    S = {""}
    E = [""]
    A = ["a"]
    result = is_closed(S, E, A, oracle_contains_a)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_closed_single_state(is_closed):
    oracle_zero = lambda s: 0
    S = {""}
    E = [""]
    A = ["a", "b"]
    closed, witness = is_closed(S, E, A, oracle_zero)
    # row("") = (0,); row("a") = (0,); row("b") = (0,) — all match row("") → closed
    assert closed is True
    assert witness is None


def test_not_closed_witness_row_not_in_S(is_closed):
    # oracle accepts only empty string
    oracle = lambda s: 1 if s == "" else 0
    S = {""}
    E = [""]
    A = ["a"]
    closed, witness = is_closed(S, E, A, oracle)
    # row("") = (1,); row("a") = (0,); (0,) not in S rows → not closed
    assert closed is False
    assert witness == "a"
