def row(s: str, E: list, oracle) -> tuple:
    """Return the row for string s: tuple of oracle(s·e) for each e in E."""
    return tuple(oracle(s + e) for e in E)


def build_table(S: set, E: list, A: list, oracle) -> dict:
    """Return observation table mapping each string in S ∪ S·A to its row."""
    S_A = {s + a for s in S for a in A}
    table = {}
    for s in S | S_A:
        table[s] = row(s, E, oracle)
    return table
