# -*- coding: utf-8 -*-
import time

import networkx as nx
from networkx.algorithms.approximation import steiner_tree

from python_interface import MS, MSR


STEINER_METHODS = ("kou", "mehlhorn")
ATTACK_METHODS = {
    "MS": MS,
    "MSR": MSR,
}


def from_networkx_to_gt(G_nx):
    from graph_tool.all import Graph

    G_gt = Graph(directed=G_nx.is_directed())
    nx2gt = {}
    static_id = G_gt.new_vertex_property("int")
    original_id = G_gt.new_vertex_property("int64_t")

    for i, node in enumerate(G_nx.nodes()):
        vertex = G_gt.add_vertex()
        nx2gt[node] = vertex
        static_id[vertex] = i
        original_id[vertex] = int(node)

    for u, v in G_nx.edges():
        G_gt.add_edge(nx2gt[u], nx2gt[v])

    G_gt.vertex_properties["static_id"] = static_id
    G_gt.vertex_properties["original_id"] = original_id
    return G_gt


def get_decycler_attack_nodes(G, attack_method="MS", stop_condition=10):
    if attack_method not in ATTACK_METHODS:
        raise ValueError(
            f"Unsupported decycler attack method: {attack_method}. "
            f"Available methods: {sorted(ATTACK_METHODS)}"
        )

    gt_graph = from_networkx_to_gt(G)
    ranked_nodes = ATTACK_METHODS[attack_method](gt_graph, stop_condition=stop_condition)
    return [node for node, score in ranked_nodes if score > 0]


def _select_steiner_terminals(attack_nodes, protection_count, terminal_factor):
    if protection_count <= 0 or not attack_nodes:
        return []

    terminal_count = min(len(attack_nodes), max(2, protection_count * terminal_factor))
    return attack_nodes[:terminal_count]


def _rank_steiner_candidates(steiner_graph, terminals, attack_nodes):
    if steiner_graph.number_of_nodes() == 0:
        return []

    attack_order = {node: idx for idx, node in enumerate(attack_nodes)}
    terminals = set(terminals)
    betweenness = nx.betweenness_centrality(steiner_graph)

    candidates = list(steiner_graph.nodes())
    candidates.sort(
        key=lambda node: (
            1 if node not in terminals else 0,
            betweenness.get(node, 0.0),
            steiner_graph.degree(node),
            -attack_order.get(node, len(attack_nodes)),
        ),
        reverse=True,
    )
    return candidates


def _build_steiner_subgraph(graph, terminals, steiner_method):
    try:
        return steiner_tree(graph, terminals, method=steiner_method)
    except TypeError:
        # Older networkx versions do not expose the `method` keyword.
        return steiner_tree(graph, terminals)


def decycler_steiner_enhancement(
    G,
    n,
    n2,
    steiner_method="kou",
    attack_method="MS",
    stop_condition=10,
    terminal_factor=2,
):
    if steiner_method not in STEINER_METHODS:
        raise ValueError(
            f"Unsupported Steiner method: {steiner_method}. "
            f"Available methods: {list(STEINER_METHODS)}"
        )

    if n2 <= 0:
        return [], 0.0

    graph = G.copy()
    time_start = time.time()

    attack_nodes = get_decycler_attack_nodes(
        graph,
        attack_method=attack_method,
        stop_condition=stop_condition,
    )
    if not attack_nodes:
        elapsed = time.time() - time_start
        print(
            f"Decycler + Steiner Enhancement ({attack_method}, {steiner_method}) "
            f"is over, and took {elapsed}s"
        )
        return [], elapsed

    terminals = _select_steiner_terminals(attack_nodes, n2, terminal_factor)

    if len(terminals) <= 1:
        protected_nodes = attack_nodes[:n2]
        elapsed = time.time() - time_start
        print(
            f"Decycler + Steiner Enhancement ({attack_method}, {steiner_method}) "
            f"is over, and took {elapsed}s"
        )
        return protected_nodes, elapsed

    steiner_subgraph = _build_steiner_subgraph(graph, terminals, steiner_method)
    ranked_candidates = _rank_steiner_candidates(
        steiner_subgraph,
        terminals,
        attack_nodes,
    )

    protected_nodes = []
    seen = set()

    for node in ranked_candidates:
        if node in seen:
            continue
        seen.add(node)
        protected_nodes.append(node)
        if len(protected_nodes) >= n2:
            break

    if len(protected_nodes) < n2:
        for node in attack_nodes:
            if node in seen:
                continue
            seen.add(node)
            protected_nodes.append(node)
            if len(protected_nodes) >= n2:
                break

    elapsed = time.time() - time_start
    print(
        f"Decycler + Steiner Enhancement ({attack_method}, {steiner_method}) "
        f"is over, and took {elapsed}s"
    )
    return protected_nodes, elapsed


def decycler_steiner_kou_enhancement(
    G,
    n,
    n2,
    attack_method="MS",
    stop_condition=10,
    terminal_factor=2,
):
    return decycler_steiner_enhancement(
        G,
        n,
        n2,
        steiner_method="kou",
        attack_method=attack_method,
        stop_condition=stop_condition,
        terminal_factor=terminal_factor,
    )


def decycler_steiner_mehlhorn_enhancement(
    G,
    n,
    n2,
    attack_method="MS",
    stop_condition=10,
    terminal_factor=2,
):
    return decycler_steiner_enhancement(
        G,
        n,
        n2,
        steiner_method="mehlhorn",
        attack_method=attack_method,
        stop_condition=stop_condition,
        terminal_factor=terminal_factor,
    )
