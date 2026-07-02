def len2_oracle(w):
    return 1 if len(w) == 2 else 0


def test_consistent_single_element(is_consistent):
    ok, w = is_consistent({""}, {""}, {"a"}, len2_oracle)
    assert ok and w is None


def test_consistent_distinct_rows(is_consistent):
    # E={"","a"}: row("")=(0,0), row("a")=(0,1) -> distinct -> consistent
    ok, _ = is_consistent({"", "a"}, {"", "a"}, {"a"}, len2_oracle)
    assert ok


def test_inconsistent_detected(is_consistent):
    S, E, A = {"", "a"}, {""}, {"a"}
    ok, w = is_consistent(S, E, A, len2_oracle)
    assert not ok
    s1, s2, a, e = w

    def r(s):
        return tuple(len2_oracle(s + x) for x in sorted(E))

    # a genuine inconsistency: same row, differing extension
    assert r(s1) == r(s2)
    assert len2_oracle(s1 + a + e) != len2_oracle(s2 + a + e)


def test_make_consistent_fixes(is_consistent, make_consistent):
    E2 = make_consistent({"", "a"}, {""}, {"a"}, len2_oracle)
    ok, _ = is_consistent({"", "a"}, E2, {"a"}, len2_oracle)
    assert ok


def test_make_consistent_extends_E(make_consistent):
    E2 = make_consistent({"", "a"}, {""}, {"a"}, len2_oracle)
    assert "" in E2 and len(E2) >= 2
