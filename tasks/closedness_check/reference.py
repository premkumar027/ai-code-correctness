def is_closed(S: set, E: list, A: list, oracle) -> tuple:
    """
    Return (True, None) if the observation table is closed.
    Return (False, witness) where witness is a string in S·A whose row
    does not match any row in S.
    """
    def row(s):
        return tuple(oracle(s + e) for e in E)

    s_rows = {row(s) for s in S}
    for s in S:
        for a in A:
            t = s + a
            if row(t) not in s_rows:
                return (False, t)
    return (True, None)
