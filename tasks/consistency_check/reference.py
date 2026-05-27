def is_consistent(S: set, E: list, A: list, oracle) -> tuple:
    """
    Return (True, None) if the observation table is consistent.
    Return (False, (s1, s2, a, e)) where s1,s2 in S have the same row
    but differ on some s1·a·e vs s2·a·e.
    """
    def row(s):
        return tuple(oracle(s + e) for e in E)

    s_list = list(S)
    for i in range(len(s_list)):
        for j in range(i + 1, len(s_list)):
            s1, s2 = s_list[i], s_list[j]
            if row(s1) == row(s2):
                for a in A:
                    for e in E:
                        if oracle(s1 + a + e) != oracle(s2 + a + e):
                            return (False, (s1, s2, a, e))
    return (True, None)
