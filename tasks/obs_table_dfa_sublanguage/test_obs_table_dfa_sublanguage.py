from itertools import product


def even_oracle(w):
    return 1 if len(w) % 2 == 0 else 0


def _accepts(d, w):
    st = d["start"]
    for ch in w:
        st = d["delta"][(st, ch)]
    return st in d["accept"]


def _words(alphabet, max_len):
    words = [""]
    for n in range(1, max_len + 1):
        words += ["".join(p) for p in product(alphabet, repeat=n)]
    return words


def test_accepted_words_in_language(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    for w in _words("a", 4):
        if _accepts(d, w):
            assert even_oracle(w) == 1


def test_empty_string_acceptance_matches_oracle(build_dfa):
    d = build_dfa({"", "a"}, {""}, {"a"}, even_oracle)
    assert _accepts(d, "") == (even_oracle("") == 1)


def test_only_empty_language_is_sublanguage(build_dfa):
    only_empty = lambda w: 1 if w == "" else 0
    d = build_dfa({"", "a"}, {""}, {"a"}, only_empty)
    for w in _words("a", 3):
        if _accepts(d, w):
            assert only_empty(w) == 1
