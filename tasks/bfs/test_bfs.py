import pytest


def test_simple_graph(bfs):
    graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}
    result = bfs(graph, 'A')
    assert result[0] == 'A'
    assert set(result) == {'A', 'B', 'C', 'D'}
    # B and C must appear before D
    assert result.index('B') < result.index('D')
    assert result.index('C') < result.index('D')


def test_source_is_first(bfs):
    graph = {'X': ['Y', 'Z'], 'Y': [], 'Z': []}
    assert bfs(graph, 'X')[0] == 'X'


def test_source_in_result(bfs):
    graph = {'A': ['B'], 'B': []}
    assert 'A' in bfs(graph, 'A')


def test_single_node(bfs):
    assert bfs({'A': []}, 'A') == ['A']


def test_disconnected_graph(bfs):
    graph = {'A': ['B'], 'B': [], 'C': ['D'], 'D': []}
    result = bfs(graph, 'A')
    assert set(result) == {'A', 'B'}
    assert 'C' not in result


def test_cycle_no_infinite_loop(bfs):
    graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
    result = bfs(graph, 'A')
    assert set(result) == {'A', 'B', 'C'}
    assert len(result) == 3


def test_linear_graph_order(bfs):
    graph = {'A': ['B'], 'B': ['C'], 'C': ['D'], 'D': []}
    assert bfs(graph, 'A') == ['A', 'B', 'C', 'D']


def test_empty_graph(bfs):
    result = bfs({}, 'A')
    assert result == [] or result is None


def test_star_graph_level_order(bfs):
    graph = {'root': ['a', 'b', 'c'], 'a': [], 'b': [], 'c': []}
    result = bfs(graph, 'root')
    assert result[0] == 'root'
    assert set(result[1:]) == {'a', 'b', 'c'}


def test_large_linear_chain(bfs):
    n = 200
    graph = {str(i): [str(i + 1)] for i in range(n)}
    graph[str(n)] = []
    result = bfs(graph, '0')
    assert result == [str(i) for i in range(n + 1)]
