def test_concat_basic(prefix_concat):
    assert prefix_concat({"a"}, {"b"}) == {"ab"}


def test_concat_product(prefix_concat):
    assert prefix_concat({"a", "b"}, {"c"}) == {"ac", "bc"}


def test_concat_with_empty_string_right(prefix_concat):
    assert prefix_concat({"a"}, {""}) == {"a"}


def test_concat_with_empty_string_left(prefix_concat):
    assert prefix_concat({""}, {"a"}) == {"a"}


def test_concat_empty_set(prefix_concat):
    assert prefix_concat(set(), {"a"}) == set()


def test_concat_prefix_closed_operands(prefix_concat):
    # {"", "a"} x {"", "b"} = {"", "b", "a", "ab"}
    assert prefix_concat({"", "a"}, {"", "b"}) == {"", "a", "b", "ab"}
