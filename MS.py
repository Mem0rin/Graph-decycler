import os
import networkx as nx
from graph_tool.all import Graph
from python_interface import MSR
from python_interface import MS

def from_networkx_to_gt(G_nx):
    G_gt = Graph(directed=G_nx.is_directed())
    # 建立nx节点到gt节点的映射
    nx2gt = {}
    static_id = G_gt.new_vertex_property("int")
    original_id = G_gt.new_vertex_property("int64_t")
    for i, node in enumerate(G_nx.nodes()):
        v = G_gt.add_vertex()
        nx2gt[node] = v
        static_id[v] = i
        original_id[v] = int(node)
    # 添加边
    for u, v in G_nx.edges():
        G_gt.add_edge(nx2gt[u], nx2gt[v])
    # 添加static_id属性
    G_gt.vertex_properties["static_id"] = static_id
    G_gt.vertex_properties["original_id"] = original_id
    return G_gt

data_dir = "/home/memo/graph_projects/decycler/test_data/small"
results = {}
def MS_attack(G, n, stop_condition=100):
    g = G.copy()
    network = from_networkx_to_gt(G)
    top_nodes = MS(network, stop_condition=stop_condition)
    lcc_size = [1]
    current_lcc = 1
    for node, score in top_nodes:
        if score == 0.0:
            break
        g.remove_node(node)

        current_lcc = lcc(g) / n

        if current_lcc < 0.01:
            lcc_size.append(current_lcc)
            return lcc_size
        lcc_size.append(current_lcc)

    return lcc_size
