# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
from scipy.sparse.linalg import ArpackNoConvergence
from networkx.algorithms.approximation import min_weighted_vertex_cover
from numpy.random import shuffle
import time
try:
    from GBT import general_betweenness_centrality
except ImportError:
    general_betweenness_centrality = None

try:
    from generalized_betweenness_successors import generalized_betweenness_successors
except ImportError:
    generalized_betweenness_successors = None
from decycler_steiner_enhancement import decycler_steiner_enhancement
from decycler_steiner_enhancement import decycler_steiner_kou_enhancement
from decycler_steiner_enhancement import decycler_steiner_mehlhorn_enhancement

#################################################
# largest connected network
#################################################
def lcc(G):  # O(n)
    if len(G) == 0:
        return 0

    return max([len(c) for c in nx.connected_components(G)])

###############################
# High Degree Enhancemnt
#############################
def high_degree_enhancement(G, n, n2):
    g = G.copy()
    time_start0 = time.time()
    top_nodes = list(nx.degree_centrality(g).items())
    HD_Time = time.time() - time_start0
    print('High Degree Enhancement is over, and took {}s'.format(HD_Time))
    top_nodes.sort(key=lambda x: x[1], reverse=True)
    enhancement_nodes=[]

    for node, deg in top_nodes[:n2]:
        enhancement_nodes.append(node)
        
    return enhancement_nodes,HD_Time
###################################
# High Betweenness Enhancement
###################################
def high_betweenness_enhancement(G, n, n2):
    g = G.copy()
    time_start0 = time.time()
    top_nodes = list(nx.betweenness_centrality(g).items())
    BT_Time = time.time() - time_start0
    print('High Betweenness Enhancement is over, and took {}s'.format(BT_Time))
    top_nodes.sort(key=lambda x: x[1], reverse=True)
    enhancement_nodes=[]

    for node, bt in top_nodes[:n2]:
        enhancement_nodes.append(node)
        
    return enhancement_nodes,BT_Time

#################################################
# Collective Influence
#################################################
def collective_influence(G, node):  # second order collective influence
    s = 0
    t = G.degree(node) - 1
    for i in G.neighbors(node):
        s += t * (G.degree(i) - 1)
    return s

#######################################
# Collective influence Enhancement
#####################################
def collective_influence_enhancement(G, n, n2):
    g = G.copy()
    time_start0 = time.time()
    top_nodes = list({node: collective_influence(g, node) for node in g.nodes()}.items())
    CI_Time = time.time() - time_start0
    print('Collective Influence Enhancement is over, and took {}s'.format(CI_Time))
    
    top_nodes.sort(key=lambda x: x[1], reverse=True)
    enhancement_nodes=[]

    for node, ci in top_nodes[:n2]:
        enhancement_nodes.append(node)
        
    return enhancement_nodes,CI_Time


#################################################
# Generalized Network Dismantling
#################################################

def gnd_enhancement_1(G2, n, n2):
    enhancement_nodes=[]
    G = G2.copy()
    time_start0 = time.time()
    while len(enhancement_nodes)<=n2 and lcc(G) > 2:
        
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
            enhancement_nodes.append(v)
    GND_Time = time.time() - time_start0
    
    print('Generalized Network Dismantling Enhancement is over, and took {}s'.format(GND_Time))
    return enhancement_nodes,GND_Time
#############################################
#closeness centrality enhancement#
#############################################
def closeness_centrality_enhancement(G,n,n2):
    
    g=G.copy()
    g_1= G.copy()
    time_start0=time.time()
    top_nodes = list(nx.closeness_centrality(g).items())
    CC_Time = time.time() - time_start0
    print('Collective Centrality Enhancement is over, and took {}s'.format(CC_Time))
    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    enhancement_nodes=[]
    for node, cc in top_nodes[:n2]:
        enhancement_nodes.append(node)
    return enhancement_nodes,CC_Time
###############################################
#eigenvector centrality enhancement
###############################################
def eigenvector_centrality_enhancement(G,n,n2):
    
    g=G.copy()
    g_1= G.copy()
    time_start0=time.time()
    top_nodes = list(nx.eigenvector_centrality(g).items())
    EC_Time = time.time() - time_start0
    print('Eigenvector Centrality Enhancement is over, and took {}s'.format(EC_Time))
    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    enhancement_nodes=[]
    
    for node, ec in top_nodes[:n2]:
        enhancement_nodes.append(node)
    return enhancement_nodes,EC_Time
###############################################
#Current-flow closeness centrality enhancement
###############################################
def current_flow_closeness_centrality_enhancement(G,n,n2):
    
    g=G.copy()
    g_1= G.copy()
    time_start0=time.time()
    top_nodes = list(nx.current_flow_closeness_centrality(g).items())
    CFCC_Time = time.time() - time_start0
    print('Current-flow Closeness Centrality Enhancement is over, and took {}s'.format(CFCC_Time))
    
    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    enhancement_nodes=[]
    for node,cfcc in top_nodes[:n2]:
        enhancement_nodes.append(node)
    return enhancement_nodes,CFCC_Time
###############################################
#Current-flow betweenness centrality enhancement
###############################################
def current_flow_betweenness_centrality_enhancement(G,n,n2):
    
    g=G.copy()
    g_1= G.copy()
    
    time_start0=time.time()
    top_nodes = list(nx.current_flow_betweenness_centrality(g).items())
    CFBT_Time = time.time() - time_start0
    print('Current-flow Betweenness Centrality Enhancement is over, and took {}s'.format(CFBT_Time))
    
    top_nodes.sort(key=lambda x: x[1], reverse=True)  

    enhancement_nodes=[]
    for node,cfbt in top_nodes[:n2]:
        enhancement_nodes.append(node)
    return enhancement_nodes,CFBT_Time
###############################################
# General Betweenness Centrality
###############################################
def general_betweenness_centrality_enhancement(G, n, n2):
    if general_betweenness_centrality is None:
        raise ImportError("GBT module is required for general_betweenness_centrality_enhancement")

    g = G.copy()
    time_start0 = time.time()
    print('General Betweenness Centrality Enhancement is running...')
    top_nodes = list(general_betweenness_centrality(g).items())
    print(top_nodes)
    GBT_Time = time.time() - time_start0
    print('General Betweenness Centrality Enhancement is over, and took {}s'.format(GBT_Time))
    top_nodes.sort(key=lambda x: x[1], reverse=True)
    enhancement_nodes=[]

    for nodes, gbt in top_nodes[:n2]:
        u= nodes[0]
        v= nodes[1]
        if u not in enhancement_nodes:
            enhancement_nodes.append(u)
        if v not in enhancement_nodes:
            enhancement_nodes.append(v)
    return enhancement_nodes,GBT_Time
