def prefix_closure(S):
    """Return the smallest prefix-closed set containing S (all prefixes, nothing more)."""
    result = set()
    for w in S:
        for i in range(len(w) + 1):
            result.add(w[:i])
    return result
