def suffix_closure(E):
    """Return the smallest suffix-closed set containing E (all suffixes, nothing more)."""
    result = set()
    for w in E:
        for i in range(len(w) + 1):
            result.add(w[i:])
    return result
