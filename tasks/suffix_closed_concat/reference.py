def suffix_concat(E1, E2):
    """Elementwise concatenation: { u + v | u in E1, v in E2 }."""
    return {u + v for u in E1 for v in E2}
