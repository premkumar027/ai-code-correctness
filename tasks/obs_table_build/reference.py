def row(s, E, oracle):
    """Row of s: one oracle answer per experiment, ordered by sorted(E)."""
    return tuple(oracle(s + e) for e in sorted(E))


def build_table(S, E, A, oracle):
    """Map every string in S and in S.A to its row."""
    table = {}
    strings = set(S) | {s + a for s in S for a in A}
    for x in strings:
        table[x] = row(x, E, oracle)
    return table
