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
        "lean_property": "Prove that if the function returns index i (i >= 0), then the element at index i equals the target",
    },

    "prefix_suffix_split": {
        "algorithm": "Prefix-Suffix Split that splits a word into all possible (prefix, suffix) pairs",
        "data_structure": "strings/lists",
        "edge_cases": "empty string, single character",
        "extra_requirements": "Return a list of all (prefix, suffix) tuples where prefix + suffix equals the original word",
        "lean_property": "Prove that for every pair (p, s) in the result, p ++ s equals the original word",
    },

    

    "prefix_closed": {
        "algorithm": (
            "Prefix-closed set operations. A set S of strings is "
            "prefix-closed if every prefix of every string in S is "
            "also in S. Implement two functions: (1) is_prefix_closed(S) "
            "that returns True if S is prefix-closed, and (2) "
            "prefix_closure(S) that returns the smallest prefix-closed "
            "set containing S"
        ),
        "data_structure": "set of strings (represented as a Python set, or as List String in Lean)",
        "edge_cases": "empty set, set containing only the empty string, single string, set with duplicates",
        "extra_requirements": (
            "Treat each string as a sequence of characters. The empty "
            "string is a prefix of every string. Do not use any "
            "external libraries"
        ),
        "lean_property": (
            "Prove that prefix_closure(S) is itself prefix-closed: "
            "for every string w in prefix_closure(S) and every prefix p of w, "
            "p is also in prefix_closure(S)"
        ),
    },

    "suffix_closed": {
        "algorithm": (
            "Suffix-closed set operations. A set E of strings is "
            "suffix-closed if every suffix of every string in E is "
            "also in E. Implement two functions: (1) is_suffix_closed(E) "
            "that returns True if E is suffix-closed, and (2) "
            "suffix_closure(E) that returns the smallest suffix-closed "
            "set containing E"
        ),
        "data_structure": "set of strings (represented as a Python set, or as List String in Lean)",
        "edge_cases": "empty set, set containing only the empty string, single string, set with duplicates",
        "extra_requirements": (
            "Treat each string as a sequence of characters. The empty "
            "string is a suffix of every string. Do not use any "
            "external libraries"
        ),
        "lean_property": (
            "Prove that suffix_closure(E) is itself suffix-closed: "
            "for every string w in suffix_closure(E) and every suffix s of w, "
            "s is also in suffix_closure(E)"
        ),
    },

    "observation_table": {
        "algorithm": (
            "Observation table data structure from Angluin's L* algorithm. "
            "Given a prefix-closed set S of access strings, a suffix-closed "
            "set E of experiments, an alphabet A, and a membership oracle "
            "T: (S \u222a S\u00b7A) \u00d7 E \u2192 {0,1}, implement: "
            "(1) the row(s) function that returns the tuple "
            "(T(s\u00b7e) for e in E), and "
            "(2) a function build_table(S, E, A, oracle) that returns the "
            "full observation table as a dictionary mapping each string in "
            "S \u222a S\u00b7A to its row"
        ),
        "data_structure": "dictionaries mapping strings to tuples of 0/1 values",
        "edge_cases": (
            "empty S, empty E, E containing only the empty string, "
            "single-symbol alphabet, oracle that always returns 0"
        ),
        "extra_requirements": (
            "S\u00b7A means the set of all concatenations s\u00b7a for s in S "
            "and a in A. The oracle is a callable that takes a string and "
            "returns 0 or 1. Do not use any external libraries"
        ),
        "lean_property": (
            "Prove that for every s in S, row(s) has length equal to the "
            "size of E (i.e., the row contains exactly one entry per experiment)"
        ),
    },

    "closedness_check": {
        "algorithm": (
            "Closedness check for an observation table. An observation "
            "table (S, E, T) is closed if for every t in S\u00b7A, there "
            "exists some s in S such that row(t) = row(s). Implement "
            "is_closed(S, E, A, oracle) that returns True if the table is "
            "closed, and if not, also returns one witness string t in S\u00b7A "
            "whose row does not match any row in S"
        ),
        "data_structure": "sets and dictionaries (or List/HashMap in Lean)",
        "edge_cases": (
            "empty S\u00b7A (when S is empty or A is empty), table where every "
            "row in S\u00b7A already appears in S, table where no rows match"
        ),
        "extra_requirements": (
            "Return a tuple (is_closed, witness) where witness is None if "
            "the table is closed, otherwise a string t in S\u00b7A that "
            "violates closedness. Do not use any external libraries"
        ),
        "lean_property": (
            "Prove that if is_closed returns (True, None), then for every "
            "t in S\u00b7A there exists s in S with row(t) = row(s)"
        ),
    },

    "consistency_check": {
        "algorithm": (
            "Consistency check for an observation table. An observation "
            "table (S, E, T) is consistent if for all s1, s2 in S with "
            "row(s1) = row(s2), and for all a in A, "
            "row(s1\u00b7a) = row(s2\u00b7a). Implement "
            "is_consistent(S, E, A, oracle) that returns True if the table "
            "is consistent, and if not, also returns a witness "
            "(s1, s2, a, e) showing where consistency fails"
        ),
        "data_structure": "sets and dictionaries (or List/HashMap in Lean)",
        "edge_cases": (
            "S with a single element (trivially consistent), all rows in S "
            "distinct (trivially consistent), two equal rows that diverge "
            "after some symbol"
        ),
        "extra_requirements": (
            "Return a tuple (is_consistent, witness) where witness is None "
            "if consistent, otherwise (s1, s2, a, e) such that "
            "row(s1) = row(s2) but T(s1\u00b7a\u00b7e) \u2260 T(s2\u00b7a\u00b7e). "
            "Do not use any external libraries"
        ),
        "lean_property": (
            "Prove that if is_consistent returns (True, None), then for all "
            "s1, s2 in S with row(s1) = row(s2) and all a in A, "
            "row(s1\u00b7a) = row(s2\u00b7a)"
        ),
    },
}