import pytest


def test_simple_graph(dijkstra):
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': [],
    }
    assert dijkstra(graph, 'A') == {'A': 0, 'B': 1, 'C': 3, 'D': 4}


def test_single_node(dijkstra):
    assert dijkstra({'A': []}, 'A') == {'A': 0}


def test_disconnected_nodes(dijkstra):
    graph = {'A': [('B', 1)], 'B': [], 'C': []}
    result = dijkstra(graph, 'A')
    assert result['A'] == 0
    assert result['B'] == 1
    assert result['C'] == float('inf')


def test_source_distance_is_zero(dijkstra):
    graph = {'X': [('Y', 10)], 'Y': [('Z', 5)], 'Z': []}
    result = dijkstra(graph, 'X')
    assert result['X'] == 0


def test_empty_graph(dijkstra):
    result = dijkstra({}, 'A')
    assert result == {} or result is None


def test_two_paths_picks_shorter(dijkstra):
    graph = {
        'A': [('B', 10), ('C', 1)],
        'B': [('D', 1)],
        'C': [('B', 1)],
        'D': [],
    }
    result = dijkstra(graph, 'A')
    assert result['D'] == 3  # A→C(1)→B(1)→D(1)


def test_all_nodes_reachable(dijkstra):
    graph = {
        'A': [('B', 2)],
        'B': [('C', 3)],
        'C': [],
    }
    result = dijkstra(graph, 'A')
    assert result == {'A': 0, 'B': 2, 'C': 5}


def test_self_loop_ignored(dijkstra):
    graph = {'A': [('A', 5), ('B', 2)], 'B': []}
    result = dijkstra(graph, 'A')
    assert result['A'] == 0
    assert result['B'] == 2


def test_large_graph(dijkstra):
    n = 100
    graph = {str(i): [(str(i + 1), 1)] for i in range(n)}
    graph[str(n)] = []
    result = dijkstra(graph, '0')
    assert result['0'] == 0
    assert result[str(n)] == n


def test_unknown_source_returns_empty_or_none(dijkstra):
    graph = {'A': [('B', 1)], 'B': []}
    result = dijkstra(graph, 'Z')
    assert result == {} or result is None
