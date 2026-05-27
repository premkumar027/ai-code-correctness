import pytest


def test_found_middle(binary_search):
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_found_first(binary_search):
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_found_last(binary_search):
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_not_found(binary_search):
    assert binary_search([1, 3, 5, 7, 9], 4) == -1


def test_empty_list(binary_search):
    assert binary_search([], 5) == -1


def test_single_element_found(binary_search):
    assert binary_search([5], 5) == 0


def test_single_element_not_found(binary_search):
    assert binary_search([5], 3) == -1


def test_two_elements_first(binary_search):
    assert binary_search([1, 2], 1) == 0


def test_two_elements_second(binary_search):
    assert binary_search([1, 2], 2) == 1


def test_large_list(binary_search):
    lst = list(range(0, 10000, 2))
    assert binary_search(lst, 5000) == 2500
    assert binary_search(lst, 5001) == -1


def test_negative_numbers(binary_search):
    lst = [-10, -5, 0, 5, 10]
    assert binary_search(lst, -5) == 1
    assert binary_search(lst, 0) == 2
    assert binary_search(lst, 3) == -1


def test_duplicates_returns_a_valid_index(binary_search):
    lst = [1, 2, 2, 2, 3]
    idx = binary_search(lst, 2)
    assert lst[idx] == 2
