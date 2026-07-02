def _row(s, E, oracle):
    return tuple(oracle(s + e) for e in sorted(E))


def build_dfa(S, E, A, oracle):
    """DFA induced by a closed & consistent table. States are row tuples."""
    def r(s):
        return _row(s, E, oracle)

    states = {r(s) for s in S}
    start = r("")
    accept = {r(s) for s in S if oracle(s) == 1}
    delta = {}
    for s in S:
        for a in A:
            delta[(r(s), a)] = r(s + a)
    return {
        "states": states,
        "start": start,
        "accept": accept,
        "delta": delta,
        "alphabet": set(A),
    }
