def even_oracle(w):
    return 1 if len(w) % 2 == 0 else 0


def test_start_in_states(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    assert d["start"] in d["states"]


def test_complete(build_dfa):
    # every state has a transition for every alphabet symbol
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    for st in d["states"]:
        for a in d["alphabet"]:
            assert (st, a) in d["delta"]


def test_transition_targets_are_states(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    for (_st, _a), tgt in d["delta"].items():
        assert tgt in d["states"]


def test_two_states(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    assert len(d["states"]) == 2


def test_single_state_all_accept(build_dfa):
    ones = lambda w: 1
    d = build_dfa({""}, {""}, {"a"}, ones)
    assert len(d["states"]) == 1
    for st in d["states"]:
        assert (st, "a") in d["delta"]
