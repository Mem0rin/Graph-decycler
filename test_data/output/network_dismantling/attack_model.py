# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
from scipy.sparse.linalg import ArpackNoConvergence
from networkx.algorithms.approximation import min_weighted_vertex_cover
from numpy.random import shuffle

#################################################
# largest connected network
#################################################
def lcc(G):  # O(n)
    if len(G) == 0:
        return 0

    return max([len(c) for c in nx.connected_components(G)])

#################################################
# High Degree Attack
#################################################
def high_degree_attack_with_enhancement(G, n, n2,enhance_nodes):
    g = G.copy()
    g_1 = G.copy()

    top_nodes = list(nx.degree_centrality(g).items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)
        if node in enhance_nodes:
            lcc_size.append(lcc(g_1)/n)
            continue
        g_1.remove_node(node)  
        lcc_size.append(lcc(g_1) / n)
        
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size

def high_degree_attack(G, n, n2):
    g = G.copy()

    top_nodes = list(nx.degree_centrality(g).items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)
        
        lcc_size.append(lcc(g) / n)
        
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size
#################################################
# High Betweenness Attack
#################################################
def high_bt_attack(G, n, n2):
    g = G.copy()
    top_nodes = list(nx.betweenness_centrality(g).items())
    top_nodes.sort(key=lambda x: x[1], reverse=True)

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)  
        lcc_size.append(lcc(g) / n)
    
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size

#################################################
# Collective Influence
#################################################
def collective_influence(G, node):  # second order collective influence
    s = 0
    t = G.degree(node) - 1
    for i in G.neighbors(node):
        s += t * (G.degree(i) - 1)
    return s

#################################################
# Collective Influence Attack
#################################################
def collective_influence_attack(G, n, n2):
    g = G.copy()
    lcc_size = [1]
    top_nodes = list({node: collective_influence(g, node) for node in g.nodes()}.items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)

    for node, ci in top_nodes[:n2]:
        g.remove_node(node)
        
        lcc_size.append(lcc(g) / n)
        
        if lcc_size[-1] < 0.01:
            return lcc_size
        
    return lcc_size


#################################################
# Generalized Network Dismantling
#################################################
def gnd_enhancement_1(G2, n, n2,enhance_nodes):
    g = G2.copy()
    lcc_size = []
    G = G2.copy()
    while lcc(G) > max(2, n//1000):
        
        LCC = G.subgraph(max(nx.connected_components(G), key=len))  
        ii = {v: i for i, v in enumerate(list(LCC.nodes()))}   
 
        L = nx.laplacian_matrix(LCC)
        
        # Get the eigenvectors.
        maxiter = 1000 * L.shape[0]  
        try:
            eigenvalues, eigenvectors = eigsh(L.astype(np.float32), k=2, which='SM', maxiter=maxiter)
        except ArpackNoConvergence:
           
            exit(1)

        Fiedler = eigenvectors[:, 1]   

        H = nx.Graph()
        for u, v in LCC.edges():
            if Fiedler[ii[u]] * Fiedler[ii[v]] <= 0.0:
                H.add_edge(u, v)

        for v in H.nodes():  # calculate weight
            H.nodes[v]['weight'] = 1.0 / H.degree(v)

        cover = list(min_weighted_vertex_cover(H, weight='weight'))   
        shuffle(cover)
        
        removed_any = False
        
        # Step 4. === Delete the nodes in cover. ===
        for v in cover:
            G.remove_node(v)
            if v in enhance_nodes:
                lcc_size.append(lcc(g)/n)
                continue
            g.remove_node(v)
            lcc_size.append(lcc(g)/n)
            if len(lcc_size) >= n2:
                return lcc_size

    return lcc_size

def gnd(G2, n, n2):

    lcc_size = []
    G = G2.copy()
    while lcc(G) > max(2, n//1000):
        
        LCC = G.subgraph(max(nx.connected_components(G), key=len))  
        ii = {v: i for i, v in enumerate(list(LCC.nodes()))}   
 
        L = nx.laplacian_matrix(LCC)
        
        # Get the eigenvectors.
        maxiter = 1000 * L.shape[0]  
        try:
            eigenvalues, eigenvectors = eigsh(L.astype(np.float32), k=2, which='SM', maxiter=maxiter)
        except ArpackNoConvergence:
           
            exit(1)

        Fiedler = eigenvectors[:, 1]   

        H = nx.Graph()
        for u, v in LCC.edges():
            if Fiedler[ii[u]] * Fiedler[ii[v]] <= 0.0:
                H.add_edge(u, v)

        for v in H.nodes():  # calculate weight
            H.nodes[v]['weight'] = 1.0 / H.degree(v)

        cover = list(min_weighted_vertex_cover(H, weight='weight'))   
        shuffle(cover)
        
        removed_any = False
        
        # Step 4. === Delete the nodes in cover. ===
        for v in cover:
            G.remove_node(v)
            lcc_size.append(lcc(G)/n)
            if len(lcc_size) >= n2:
                return lcc_size

    return lcc_size
#############################################
#closeness centrality attack#
#############################################
def closeness_centrality_attack_with_enhancement(G,n,n2,enhance_nodes):
    
    g=G.copy()
    g_1= G.copy()
    
    top_nodes = list(nx.closeness_centrality(g).items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)
        if node in enhance_nodes:
            lcc_size.append(lcc(g_1)/n)
            continue
        g_1.remove_node(node)  
        lcc_size.append(lcc(g_1) / n)
        
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size
###############################################
#eigenvector centrality attack
###############################################
def eigenvector_centrality_attack_with_enhancement(G,n,n2,enhance_nodes):
    
    g=G.copy()
    g_1= G.copy()
    top_nodes = list(nx.eigenvector_centrality(g).items())

    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    lcc_size = [1]
    for node, deg in top_nodes[:n2]:
        g.remove_node(node)
        if node in enhance_nodes:
            lcc_size.append(lcc(g_1)/n)
            continue
        g_1.remove_node(node)  
        lcc_size.append(lcc(g_1) / n)
        
        if lcc_size[-1] < 0.01:
            return lcc_size
    
    return lcc_size
###############################################
#Min-Sum attack
###############################################

