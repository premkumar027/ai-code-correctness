import pytest


# Oracle: accepts strings that contain 'a' (simple DFA for testing)
def oracle_contains_a(s):
    return 1 if 'a' in s else 0


def test_row_length_equals_E(row):
    E = ["", "a", "b"]
    result = row("s", E, oracle_contains_a)
    assert len(result) == len(E)


def test_row_is_tuple(row):
    E = ["", "a"]
    result = row("x", E, oracle_contains_a)
    assert isinstance(result, tuple)


def test_row_correct_values(row):
    E = ["", "a", "b"]
    # "s" + "" = "s" → 0; "s" + "a" = "sa" → 1; "s" + "b" = "sb" → 0
    result = row("s", E, oracle_contains_a)
    assert result == (0, 1, 0)


def test_row_empty_string(row):
    E = ["", "a"]
    result = row("", E, oracle_contains_a)
    assert result == (0, 1)


def test_row_empty_E(row):
    result = row("abc", [], oracle_contains_a)
    assert result == ()


def test_build_table_keys(build_table):
    S = {"", "a"}
    E = ["", "b"]
    A = ["a", "b"]
    table = build_table(S, E, A, oracle_contains_a)
    # S·A = {""+"a",""+b","a"+"a","a"+"b"} = {"a","b","aa","ab"}
    # S ∪ S·A = {"", "a", "b", "aa", "ab"}
    expected_keys = {"", "a", "b", "aa", "ab"}
    assert expected_keys.issubset(set(table.keys()))


def test_build_table_values_are_tuples(build_table):
    S = {""}
    E = ["", "a"]
    A = ["a"]
    table = build_table(S, E, A, oracle_contains_a)
    for v in table.values():
        assert isinstance(v, tuple)


def test_build_table_row_length(build_table):
    S = {"", "a"}
    E = ["", "a", "b"]
    A = ["a"]
    table = build_table(S, E, A, oracle_contains_a)
    for v in table.values():
        assert len(v) == len(E)


def test_build_table_oracle_always_zero(build_table):
    oracle_zero = lambda s: 0
    S = {"", "a"}
    E = ["", "a"]
    A = ["b"]
    table = build_table(S, E, A, oracle_zero)
    for v in table.values():
        assert all(x == 0 for x in v)


def test_build_table_single_symbol_alphabet(build_table):
    S = {""}
    E = [""]
    A = ["a"]
    table = build_table(S, E, A, oracle_contains_a)
    assert "" in table
    assert "a" in table
