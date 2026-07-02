def test_closure_basic(prefix_closure):
    assert prefix_closure({"ab"}) == {"", "a", "ab"}


def test_closure_multiple(prefix_closure):
    assert prefix_closure({"ab", "cd"}) == {"", "a", "ab", "c", "cd"}


def test_closure_empty_set(prefix_closure):
    assert prefix_closure(set()) == set()


def test_closure_empty_string(prefix_closure):
    assert prefix_closure({""}) == {""}


def test_closure_single_char(prefix_closure):
    assert prefix_closure({"a"}) == {"", "a"}


def test_closure_output_is_prefix_closed(prefix_closure, is_prefix_closed):
    assert is_prefix_closed(prefix_closure({"abc", "xy"}))


def test_is_prefix_closed_true(is_prefix_closed):
    assert is_prefix_closed({"", "a", "ab"})


def test_is_prefix_closed_false(is_prefix_closed):
    assert not is_prefix_closed({"ab"})  # missing "" and "a"


def test_is_prefix_closed_empty_set(is_prefix_closed):
    assert is_prefix_closed(set())


def test_is_prefix_closed_empty_string(is_prefix_closed):
    assert is_prefix_closed({""})
