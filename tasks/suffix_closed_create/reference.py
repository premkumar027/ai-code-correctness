def is_suffix_closed(E):
    """Return True if every suffix of every string in E is also in E."""
    E = set(E)
    for w in E:
        for i in range(len(w) + 1):
            if w[i:] not in E:
                return False
    return True


def suffix_closure(E):
    """Return the smallest suffix-closed set containing E (all suffixes)."""
    result = set()
    for w in E:
        for i in range(len(w) + 1):
            result.add(w[i:])
    return result
