TASKS = {
    "dijkstra": {
        "algorithm": "Dijkstra's shortest path algorithm",
        "data_structure": "adjacency list with a min-heap",
        "edge_cases": "empty graph, disconnected nodes, single node",
        "extra_requirements": "Return a dictionary mapping each node to its shortest distance from the source",
        "lean_property": "Prove that the distance to the source node is always 0",
    },

    "bfs": {
        "algorithm": "Breadth-First Search (BFS) traversal",
        "data_structure": "adjacency list with a queue",
        "edge_cases": "empty graph, cycles, disconnected nodes, single node",
        "extra_requirements": "Return the list of visited nodes in BFS order",
        "lean_property": "Prove that the source node is always in the visited list",
    },

    "merge_sort": {
        "algorithm": "Merge Sort",
        "data_structure": "list/array",
        "edge_cases": "empty list, single element, already sorted, reverse sorted, duplicates",
        "extra_requirements": "Implement both the merge and mergeSort functions separately",
        "lean_property": "Prove that the length of the sorted list equals the length of the input list",
    },

    "binary_search": {
        "algorithm": "Binary Search",
        "data_structure": "sorted list/array",
        "edge_cases": "empty list, single element, target not found, target at first/last position",
        "extra_requirements": "Return the index if found, -1 if not found",
        "lean_property": "Prove that if the function returns index i, then the element at index i equals the target",
    },

    "prefix_suffix": {
        "algorithm": "Prefix-Suffix Split that splits a word into all possible (prefix, suffix) pairs",
        "data_structure": "strings/lists",
        "edge_cases": "empty string, single character",
        "extra_requirements": "Return a list of all (prefix, suffix) tuples where prefix + suffix equals the original word",
        "lean_property": "Prove that for every pair (p, s) in the result, p ++ s equals the original word",
    },
}