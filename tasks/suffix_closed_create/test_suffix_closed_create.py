def test_closure_basic(suffix_closure):
    assert suffix_closure({"ab"}) == {"", "b", "ab"}


def test_closure_multiple(suffix_closure):
    assert suffix_closure({"ab", "cd"}) == {"", "b", "ab", "d", "cd"}


def test_closure_empty_set(suffix_closure):
    assert suffix_closure(set()) == set()


def test_closure_empty_string(suffix_closure):
    assert suffix_closure({""}) == {""}


def test_closure_single_char(suffix_closure):
    assert suffix_closure({"a"}) == {"", "a"}


def test_closure_output_is_suffix_closed(suffix_closure, is_suffix_closed):
    assert is_suffix_closed(suffix_closure({"abc", "xy"}))


def test_is_suffix_closed_true(is_suffix_closed):
    assert is_suffix_closed({"", "b", "ab"})


def test_is_suffix_closed_false(is_suffix_closed):
    assert not is_suffix_closed({"ab"})  # missing "" and "b"


def test_is_suffix_closed_empty_set(is_suffix_closed):
    assert is_suffix_closed(set())


def test_is_suffix_closed_empty_string(is_suffix_closed):
    assert is_suffix_closed({""})
