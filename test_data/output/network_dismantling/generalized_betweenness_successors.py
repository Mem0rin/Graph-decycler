
import networkx as nx
from collections import deque

def count_shortest_paths(g, source):
    # 返回从source到所有节点的最短路径条数和距离
    sigma = {v: 0 for v in g.nodes}
    dist = {v: -1 for v in g.nodes}
    sigma[source] = 1
    dist[source] = 0
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in g.neighbors(v):
            if dist[w] < 0:
                dist[w] = dist[v] + 1
                queue.append(w)
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
    return sigma, dist

def count_paths_through_node(g, source, target, node, sigma, dist):
    # 统计从source到target的所有最短路径中，经过node的条数
    if node == source or node == target:
        return 0
    # 逆序累加法
    stack = []
    pred = {v: [] for v in g.nodes}
    for v in g.nodes:
        for w in g.neighbors(v):
            if dist[w] == dist[v] + 1:
                pred[w].append(v)
    # 只统计最短路径
    delta = {v: 0 for v in g.nodes}
    stack = [target]
    visited = set()
    while stack:
        w = stack.pop()
        if w in visited:
            continue
        visited.add(w)
        for v in pred[w]:
            if w == node:
                delta[v] += sigma[v]
            else:
                delta[v] += delta[w]
            stack.append(v)
    return delta[source]

def generalized_betweenness_successors(g):
    result = {}
    nodes = list(g.nodes)
    for v in nodes:
        for w in g.neighbors(v):
            gb = 0.0
            for s in nodes:
                if s == v or s == w:
                    continue
                sigma, dist = count_shortest_paths(g, s)
                count_sv = sigma[v]
                count_sw = sigma[w]
                if count_sw == 0:
                    continue
                for t in nodes:
                    if t == w:
                        gb += count_sv / count_sw
                    else:
                        count_st = sigma[t]
                        if count_st == 0:
                            continue
                        # 限制条件：v和w必须在s到t的最短路径上
                        # 计算dsv, dsw, dvt, dwt, dst
                        dsv = dist[v]
                        dsw = dist[w]
                        dvt = -1
                        dwt = -1
                        dist_t, _ = count_shortest_paths(g, t)
                        if v in dist_t:
                            dvt = dist_t[v]
                        if w in dist_t:
                            dwt = dist_t[w]
                        dst = dist[t]
                        # 判断条件
                        if (dsv + 1 + dwt != dst) and (dsw + 1 + dvt != dst):
                            continue
                        count_st_w = count_paths_through_node(g, s, t, w, sigma, dist)
                        gb += (count_sv / count_sw) * (count_st_w / count_st)
            result[(v, w)] = gb
    return result


