def is_prefix_closed(S: set) -> bool:
    """Return True if every prefix of every string in S is also in S."""
    for word in S:
        for i in range(len(word)):
            if word[:i] not in S:
                return False
    return True


def prefix_closure(S: set) -> set:
    """Return the smallest prefix-closed set containing S."""
    result = set()
    for word in S:
        for i in range(len(word) + 1):
            result.add(word[:i])
    return result
