def even_oracle(w):
    return 1 if len(w) % 2 == 0 else 0


def test_row_length(row):
    assert len(row("a", {"", "x"}, even_oracle)) == 2


def test_row_values(row):
    # sorted(E) = ["", "x"]; "a"->len1->0, "ax"->len2->1
    assert row("a", {"", "x"}, even_oracle) == (0, 1)


def test_row_empty_E(row):
    assert row("a", set(), even_oracle) == ()


def test_build_table_keys(build_table):
    t = build_table({"", "a"}, {""}, {"a"}, even_oracle)
    assert set(t.keys()) == {"", "a", "aa"}  # S union S.A


def test_build_table_row_length(build_table):
    t = build_table({"", "a"}, {"", "b"}, {"a"}, even_oracle)
    assert all(len(r) == 2 for r in t.values())


def test_build_table_values(build_table):
    t = build_table({""}, {""}, {"a"}, even_oracle)
    assert t[""] == (1,) and t["a"] == (0,)


def test_build_table_empty_S(build_table):
    assert build_table(set(), {""}, {"a"}, even_oracle) == {}


def test_build_table_oracle_all_zero(build_table):
    zero = lambda w: 0
    t = build_table({"", "a"}, {""}, {"a"}, zero)
    assert all(r == (0,) for r in t.values())
