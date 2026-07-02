def row(s, E, oracle):
    return tuple(oracle(s + e) for e in sorted(E))


def is_consistent(S, E, A, oracle):
    """(True, None) if consistent, else (False, (s1, s2, a, e)) witnessing failure."""
    S = list(S)
    for s1 in S:
        for s2 in S:
            if row(s1, E, oracle) == row(s2, E, oracle):
                for a in A:
                    if row(s1 + a, E, oracle) != row(s2 + a, E, oracle):
                        for e in sorted(E):
                            if oracle(s1 + a + e) != oracle(s2 + a + e):
                                return (False, (s1, s2, a, e))
    return (True, None)


def make_consistent(S, E, A, oracle):
    """Add distinguishing experiments a+e to E until the table is consistent."""
    E = set(E)
    while True:
        ok, witness = is_consistent(S, E, A, oracle)
        if ok:
            return E
        s1, s2, a, e = witness
        E.add(a + e)
