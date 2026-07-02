def test_closure_exact_no_extras(suffix_closure):
    # equality catches any string beyond the minimal suffix set
    assert suffix_closure({"ab"}) == {"", "b", "ab"}


def test_closure_no_unrelated(suffix_closure):
    assert "a" not in suffix_closure({"ab"})


def test_closure_longer(suffix_closure):
    assert suffix_closure({"abc"}) == {"", "c", "bc", "abc"}


def test_closure_empty_set(suffix_closure):
    assert suffix_closure(set()) == set()


def test_closure_empty_string(suffix_closure):
    assert suffix_closure({""}) == {""}


def test_closure_idempotent(suffix_closure):
    once = suffix_closure({"ab", "cd"})
    assert suffix_closure(once) == once
