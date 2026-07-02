def test_accepts_member(make_oracle):
    o = make_oracle({"a", "ab"})
    assert o("a") == 1 and o("ab") == 1


def test_rejects_nonmember(make_oracle):
    o = make_oracle({"a"})
    assert o("b") == 0 and o("") == 0


def test_empty_language(make_oracle):
    o = make_oracle(set())
    assert o("") == 0 and o("a") == 0


def test_empty_string_accepted(make_oracle):
    o = make_oracle({""})
    assert o("") == 1 and o("a") == 0


def test_returns_zero_or_one(make_oracle):
    o = make_oracle({"x"})
    assert o("x") in (0, 1) and o("y") in (0, 1)
