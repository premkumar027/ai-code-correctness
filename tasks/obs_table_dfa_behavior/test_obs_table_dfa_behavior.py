def even_oracle(w):
    return 1 if len(w) % 2 == 0 else 0


def _run(d, w):
    st = d["start"]
    for ch in w:
        st = d["delta"][(st, ch)]
    return st


def _row(s, E, oracle):
    return tuple(oracle(s + e) for e in sorted(E))


def test_run_reaches_row_for_access_strings(build_dfa):
    S, E, A = {"", "a"}, {""}, {"a"}
    d = build_dfa(S, E, A, even_oracle)
    for s in S:
        assert _run(d, s) == _row(s, E, even_oracle)


def test_run_empty_is_start(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    assert _run(d, "") == d["start"]


def test_run_multistep_matches_row(build_dfa):
    E = {""}
    d = build_dfa({"", "a"}, E, {"a"}, even_oracle)
    assert _run(d, "aa") == _row("aa", E, even_oracle)
