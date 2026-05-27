def prefix_suffix_split(word: str) -> list[tuple[str, str]]:
    """Return all (prefix, suffix) pairs where prefix + suffix == word."""
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]
