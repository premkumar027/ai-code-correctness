import pytest
import random


def test_sort_basic(merge_sort):
    assert merge_sort([3, 1, 2]) == [1, 2, 3]


def test_sort_empty(merge_sort):
    assert merge_sort([]) == []


def test_sort_single(merge_sort):
    assert merge_sort([42]) == [42]


def test_sort_already_sorted(merge_sort):
    assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_sort_reverse(merge_sort):
    assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_sort_duplicates(merge_sort):
    assert merge_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]


def test_sort_all_equal(merge_sort):
    assert merge_sort([7, 7, 7]) == [7, 7, 7]


def test_sort_preserves_length(merge_sort):
    lst = [5, 3, 8, 1, 9, 2]
    assert len(merge_sort(lst)) == len(lst)


def test_sort_does_not_mutate_input(merge_sort):
    lst = [3, 1, 2]
    original = lst[:]
    merge_sort(lst)
    assert lst == original


def test_sort_large(merge_sort):
    lst = list(range(500, 0, -1))
    assert merge_sort(lst) == list(range(1, 501))


def test_merge_two_sorted(merge):
    assert merge([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]


def test_merge_one_empty(merge):
    assert merge([], [1, 2, 3]) == [1, 2, 3]
    assert merge([1, 2, 3], []) == [1, 2, 3]


def test_merge_both_empty(merge):
    assert merge([], []) == []


def test_merge_single_elements(merge):
    assert merge([1], [2]) == [1, 2]
    assert merge([2], [1]) == [1, 2]
