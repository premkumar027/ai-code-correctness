def test_concat_basic(suffix_concat):
    assert suffix_concat({"a"}, {"b"}) == {"ab"}


def test_concat_product(suffix_concat):
    assert suffix_concat({"a", "b"}, {"c"}) == {"ac", "bc"}


def test_concat_with_empty_string_right(suffix_concat):
    assert suffix_concat({"a"}, {""}) == {"a"}


def test_concat_with_empty_string_left(suffix_concat):
    assert suffix_concat({""}, {"a"}) == {"a"}


def test_concat_empty_set(suffix_concat):
    assert suffix_concat(set(), {"a"}) == set()


def test_concat_suffix_closed_operands(suffix_concat):
    # {"", "a"} x {"", "b"} = {"", "b", "a", "ab"}
    assert suffix_concat({"", "a"}, {"", "b"}) == {"", "a", "b", "ab"}
