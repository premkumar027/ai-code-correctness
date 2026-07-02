def even_oracle(w):
    return 1 if len(w) % 2 == 0 else 0


def test_closed_true(is_closed):
    ok, w = is_closed({"", "a"}, {""}, {"a"}, even_oracle)
    assert ok and w is None


def test_closed_false_with_witness(is_closed):
    # S={""}: row("")=(1); S.A={"a"}, row("a")=(0) not among S rows -> (False, "a")
    ok, w = is_closed({""}, {""}, {"a"}, even_oracle)
    assert not ok and w == "a"


def test_empty_alphabet_is_closed(is_closed):
    ok, w = is_closed({""}, {""}, set(), even_oracle)
    assert ok and w is None


def test_close_table_makes_closed(is_closed, close_table):
    S2 = close_table({""}, {""}, {"a"}, even_oracle)
    ok, _ = is_closed(S2, {""}, {"a"}, even_oracle)
    assert ok


def test_close_table_extends(close_table):
    S2 = close_table({""}, {""}, {"a"}, even_oracle)
    assert "" in S2 and "a" in S2


def test_close_table_already_closed(close_table):
    S2 = close_table({"", "a"}, {""}, {"a"}, even_oracle)
    assert {"", "a"} <= S2
