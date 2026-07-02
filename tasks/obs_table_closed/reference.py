def row(s, E, oracle):
    return tuple(oracle(s + e) for e in sorted(E))


def is_closed(S, E, A, oracle):
    """(True, None) if closed, else (False, t) for a violating t in S.A."""
    S = set(S)
    s_rows = {row(s, E, oracle) for s in S}
    for s in S:
        for a in A:
            t = s + a
            if row(t, E, oracle) not in s_rows:
                return (False, t)
    return (True, None)


def close_table(S, E, A, oracle):
    """Extend S with violating S.A strings until the table is closed."""
    S = set(S)
    while True:
        ok, witness = is_closed(S, E, A, oracle)
        if ok:
            return S
        S.add(witness)
