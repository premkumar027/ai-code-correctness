from collections import deque


def bfs(graph: dict, source: str) -> list:
    """Return nodes in BFS order starting from source."""
    if not graph or source not in graph:
        return []
    visited = []
    seen = {source}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbour in graph[node]:
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return visited
