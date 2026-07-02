def is_prefix_closed(S):
    """Return True if every prefix of every string in S is also in S."""
    S = set(S)
    for w in S:
        for i in range(len(w) + 1):
            if w[:i] not in S:
                return False
    return True


def prefix_closure(S):
    """Return the smallest prefix-closed set containing S (all prefixes)."""
    result = set()
    for w in S:
        for i in range(len(w) + 1):
            result.add(w[:i])
    return result
