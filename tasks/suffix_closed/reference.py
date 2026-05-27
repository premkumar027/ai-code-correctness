def is_suffix_closed(E: set) -> bool:
    """Return True if every suffix of every string in E is also in E."""
    for word in E:
        for i in range(1, len(word) + 1):
            if word[i:] not in E:
                return False
    return True


def suffix_closure(E: set) -> set:
    """Return the smallest suffix-closed set containing E."""
    result = set()
    for word in E:
        for i in range(len(word) + 1):
            result.add(word[i:])
    return result
