import heapq


def dijkstra(graph: dict, source: str) -> dict:
    """Return shortest distances from source to every node in graph."""
    if not graph:
        return {}
    distances = {node: float('inf') for node in graph}
    if source not in distances:
        return {}
    distances[source] = 0
    heap = [(0, source)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distances[node]:
            continue
        for neighbour, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                heapq.heappush(heap, (new_dist, neighbour))
    return distances
