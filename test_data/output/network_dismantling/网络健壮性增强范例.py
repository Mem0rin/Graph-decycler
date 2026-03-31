# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 17:37:52 2025

@author: Administrator
"""

import networkx as nx
import numpy as np

import matplotlib.pyplot as plt

def lcc(G):  # O(n)
    if len(G) == 0:
        return 0

    return max([len(c) for c in nx.connected_components(G)])

def high_bt_attack(G, n, n2):
    g = G.copy()

    top_nodes = list(nx.betweenness_centrality(g).items())#介数中心性
    top_nodes.sort(key=lambda x: x[1], reverse=True)

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)  
        lcc_size.append(lcc(g) / n)
    
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size
def high_degree_select(G):
    g = G.copy()

    top_nodes = list(nx.degree_centrality(g).items())
    top_nodes.sort(key=lambda x: x[1], reverse=True)
    
    return top_nodes
#################################################
# High Degree Attack
#################################################
def high_degree_attack(G, n, n2):
    g = G.copy()#复制一个，不影响G

    top_nodes = list(nx.degree_centrality(g).items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)  #排序

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)  #攻击一次
        lcc_size.append(lcc(g) / n)#最大规模/n
        
        if lcc_size[-1] < 0.01:#如果低于0.01马上退出并输出，没有就等到遍历完在输出
            return lcc_size
    
    return lcc_size

def high_bt_attack_with_enhancement(G, n, n2, enhance_ratio=0.1):
    """
    高度攻击算法（节点增强版）

    Args:
        G: 网络图
        n: 网络节点总数
        n2: 攻击节点数
        enhance_ratio: 增强节点比例

    Returns:
        lcc_size: 最大连通子图比例列表
    """

    g = G.copy()

    # 随机选择增强节点
    num_enhance_nodes = int(n * enhance_ratio)#增强节点总数
    enhance_nodes = high_degree_select(g)[:num_enhance_nodes]#取增强节点

    top_nodes = list(nx.betweenness_centrality(g).items())
    top_nodes.sort(key=lambda x: x[1], reverse=True)

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        # 如果节点是增强节点，则跳过
        if node in enhance_nodes:
            continue
        g.remove_node(node)
        lcc_size.append(lcc(g) / n)

        if lcc_size[-1] < 0.01:
            return lcc_size

    return lcc_size

def create_ba_network(n, m):
    """
    创建 BA 网络

    Args:
        n: 节点数量
        m: 每个新节点连接的已有节点数

    Returns:
        G: BA 网络
    """

    G = nx.barabasi_albert_graph(n, m)
    return G

def plot_lcc_changes(lcc_size):
    """
    绘制 LCC 变化曲线

    Args:
        lcc_size: LCC 比例列表
    """

    plt.plot(range(len(lcc_size)), lcc_size, marker='o')
    plt.xlabel('attacked nodes')
    plt.ylabel('lcc size (%)')
    plt.title('robust curve')
    plt.grid(True)
    plt.show()
    
def plot_lcc_changes2(lcc_size_with_enhancement, lcc_size_without_enhancement):
    """绘制 LCC 变化曲线"""
    plt.plot(range(len(lcc_size_with_enhancement)), lcc_size_with_enhancement, marker='o', label='enforced')
    plt.plot(range(len(lcc_size_without_enhancement)), lcc_size_without_enhancement, marker='x', label='without')
    plt.xlabel('attacked nodes')
    plt.ylabel('lcc size (%)')
    plt.title('robust curve')
    plt.legend()
    plt.grid(True)
    plt.show()

# 创建 BA 网络
G = create_ba_network(1000, 3)

lcc_size_without_enhancement = high_bt_attack(G.copy(), 1000, 300)


# 进行攻击，增强 10% 的节点
lcc_size = high_bt_attack_with_enhancement(G, 1000, 900, 0.1)

# 绘制 LCC 变化曲线
plot_lcc_changes2(lcc_size, lcc_size_without_enhancement)