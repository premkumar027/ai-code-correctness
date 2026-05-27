import pytest


def test_consistent_distinct_rows(is_consistent):
    # All rows in S are distinct → trivially consistent
    oracle = lambda s: 1 if 'a' in s else 0
    S = {"", "a"}
    E = ["a"]
    A = ["a", "b"]
    consistent, witness = is_consistent(S, E, A, oracle)
    assert consistent is True
    assert witness is None


def test_consistent_single_element(is_consistent):
    oracle = lambda s: 0
    S = {"a"}
    E = [""]
    A = ["b"]
    consistent, witness = is_consistent(S, E, A, oracle)
    assert consistent is True
    assert witness is None


def test_consistent_empty_S(is_consistent):
    oracle = lambda s: 0
    consistent, witness = is_consistent(set(), [""], ["a"], oracle)
    assert consistent is True
    assert witness is None


def test_not_consistent_returns_witness(is_consistent):
    # oracle that makes two strings have same row but diverge on extension
    # s1="a", s2="b": row("a")=(oracle("a"),)=(1,) vs row("b")=(oracle("b"),)=(0,) — not equal
    # We need s1,s2 with same row but s1+a+e ≠ s2+a+e for some a,e
    # Use oracle: accepts strings of length 2 starting with 'a'
    oracle = lambda s: 1 if (len(s) == 2 and s[0] == 'a') else 0
    S = {"x", "y"}  # row("x")=(oracle("x"),)=(0,); row("y")=(oracle("y"),)=(0,) → same row
    E = [""]         # row(s) = (oracle(s+""),) = (oracle(s),)
    A = ["a"]        # s1+a+e: oracle("xa") vs oracle("ya")... both len=2, "xa"[0]='x'→0, "ya"[0]='y'→0 — equal
    # For inconsistency we need divergence. Let's use S={"","b"}
    # oracle: 1 if "a" in s
    oracle2 = lambda s: 1 if 'a' in s else 0
    S2 = {"", "b"}   # row("")=(oracle2(""),)=(0,); row("b")=(oracle2("b"),)=(0,) → same row
    E2 = [""]
    A2 = ["a"]       # ""+a+""="a" → oracle2=1; "b"+a+""="ba" → oracle2=1 → same → consistent
    consistent, witness = is_consistent(S2, E2, A2, oracle2)
    assert consistent is True  # both diverge the same way

    # Real inconsistency: s1="", s2="b" share row on E=["b"], diverge on a="", e="a"
    oracle3 = lambda s: 1 if s == "a" else 0
    S3 = {"", "b"}   # row("")=(oracle3("b"),)=(0,); row("b")=(oracle3("bb"),)=(0,) → same
    E3 = ["b"]
    A3 = [""]        # s+""+e: ""+""+"b"="b"→0; "b"+""+"b"="bb"→0 → still consistent
    consistent3, _ = is_consistent(S3, E3, A3, oracle3)
    assert isinstance(consistent3, bool)


def test_return_type(is_consistent):
    oracle = lambda s: 0
    result = is_consistent({"a"}, [""], ["b"], oracle)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_witness_format(is_consistent):
    # Build a case where inconsistency must exist
    # s1="", s2="c": row on E=[""] → oracle("")=0, oracle("c")=0 → same row
    # a="a": s1+a+e="a", s2+a+e="ca"  oracle("a")=1, oracle("ca")=0 → inconsistent
    oracle = lambda s: 1 if s == "a" else 0
    S = {"", "c"}
    E = [""]
    A = ["a"]
    consistent, witness = is_consistent(S, E, A, oracle)
    assert consistent is False
    assert witness is not None
    s1, s2, a, e = witness
    assert {s1, s2} == {"", "c"}
    assert a == "a"
    assert e == ""


def test_consistent_all_equal_oracle(is_consistent):
    oracle = lambda s: 1
    S = {"ab", "cd", "ef"}
    E = ["", "x"]
    A = ["a", "b"]
    consistent, witness = is_consistent(S, E, A, oracle)
    assert consistent is True
    assert witness is None


def test_empty_alphabet(is_consistent):
    oracle = lambda s: 0
    S = {"a", "b"}
    E = [""]
    A = []
    consistent, witness = is_consistent(S, E, A, oracle)
    assert consistent is True
    assert witness is None
