def test_closure_exact_no_extras(prefix_closure):
    # equality catches any string beyond the minimal prefix set
    assert prefix_closure({"ab"}) == {"", "a", "ab"}


def test_closure_no_unrelated(prefix_closure):
    assert "b" not in prefix_closure({"ab"})


def test_closure_longer(prefix_closure):
    assert prefix_closure({"abc"}) == {"", "a", "ab", "abc"}


def test_closure_empty_set(prefix_closure):
    assert prefix_closure(set()) == set()


def test_closure_empty_string(prefix_closure):
    assert prefix_closure({""}) == {""}


def test_closure_idempotent(prefix_closure):
    once = prefix_closure({"ab", "cd"})
    assert prefix_closure(once) == once
