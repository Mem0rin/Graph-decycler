import heapq
import sys
import networkx as nx

# quick and dirty graph implementation: removed nodes are just flagged

def lcc(G):  # O(n)
    if len(G) == 0:
        return 0

    return max([len(c) for c in nx.connected_components(G)])



class Graph:
    V = []
    present = []
    M = 0

    def size(self):
        return sum(self.present)

    def add_node(self, i):
        if i >= len(self.V):
            delta = i + 1 - len(self.V)
            self.present += [1] * delta
            self.V += [[] for j in range(delta)]

    def add_edge(self, i, j):
        self.add_node(i)
        self.add_node(j)
        self.V[i] += [j]
        self.V[j] += [i]
        self.M += 1

    def remove_node(self, i):
        self.present[i] = 0
        self.M -= sum(1 for j in self.V[i] if self.present[j])


def lccG(G):
    """将自定义Graph G转为networkx.Graph并计算最大连通分量"""
    import networkx as nx
    nxG = nx.Graph()
    for i, nbrs in enumerate(G.V):
        if G.present[i]:
            nxG.add_node(i)
            for j in nbrs:
                if G.present[j]:
                    nxG.add_edge(i, j)
    if nxG.number_of_nodes() == 0:
        return 0
    return max(len(c) for c in nx.connected_components(nxG))


def compute_lcc_size(G):
    """Compute largest connected component size for the custom Graph G.

    G.V is adjacency list, G.present marks nodes still present (1) or removed (0).
    This performs a simple DFS/BFS over present nodes.
    """
    if sum(G.present) == 0:
        return 0

    visited = [False] * len(G.V)
    max_size = 0

    for u in range(len(G.V)):
        if G.present[u] and not visited[u]:
            # DFS stack
            stack = [u]
            visited[u] = True
            cnt = 0
            while stack:
                v = stack.pop()
                cnt += 1
                for w in G.V[v]:
                    if G.present[w] and not visited[w]:
                        visited[w] = True
                        stack.append(w)
            if cnt > max_size:
                max_size = cnt

    return max_size


G = Graph()

n = 0
for l in sys.stdin:
    v = l.split()
    if v[0] == "D" or v[0] == "E":
        G.add_edge(int(v[1]), int(v[2]))
    if v[0] == "V":
        G.add_node(int(v[1]))
    if v[0] == "S":
        G.remove_node(int(v[1]))
        n += 1
        
print("{}".format(lccG(G)))
N = G.size()
S = [0] * len(G.V)


def size(i, j):
    if not G.present[i]:
        return 0
    if S[i] != 0:
        # print("# the graph is NOT acyclic")
        # exit()
        print(i, S[i], j)
        exit("the graph is NOT acyclic")
    S[i] = 1 + sum(size(k, i) for k in G.V[i] if (k != j and G.present[k]))
    return S[i]


H = [(-size(i, None), i) for i in range(len(G.V)) if G.present[i] and not S[i]]

Ncc = len(H)
# print("# N:", N, "Ncc:", Ncc, "M:", G.M)
assert N - Ncc == G.M

# print("# the graph is acyclic")

sys.stdout.flush()

heapq.heapify(H)
while len(H):
    s, i = heapq.heappop(H)
    scomp = -s
    sender = None
    while True:
        sizes = [(S[k], k) for k in G.V[i] if k != sender and G.present[k]]
        if len(sizes) == 0:
            break
        M, largest = max(sizes)
        if M <= scomp / 2:
            for k in G.V[i]:
                if S[k] > 1 and G.present[k]:
                    heapq.heappush(H, (-S[k], k))
            G.remove_node(i)
            n += 1
            # compute lcc_size on the current graph state (after removal)
            lcc_size = compute_lcc_size(G)
            lcc_size2 = lccG(G)
            # print node index, removal count, scomp (subtree comp size), and current LCC size
            print("S {} {} {} {} {}".format(i, n, scomp, lcc_size, lcc_size2))
            if scomp <= int(sys.argv[1]):
                exit()
            sys.stdout.flush()
            break
        S[i] = 1 + sum(S[k] for k in G.V[i] if k != largest and G.present[k])
        sender, i = i, largest
