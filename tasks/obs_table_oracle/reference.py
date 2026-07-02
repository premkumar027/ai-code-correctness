def make_oracle(accepted):
    """Return a membership oracle answering 1 iff the word is in `accepted`."""
    accepted = set(accepted)

    def oracle(word):
        return 1 if word in accepted else 0

    return oracle
