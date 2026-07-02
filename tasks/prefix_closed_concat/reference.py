def prefix_concat(S1, S2):
    """Elementwise concatenation: { u + v | u in S1, v in S2 }."""
    return {u + v for u in S1 for v in S2}
