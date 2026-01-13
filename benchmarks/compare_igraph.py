import time
import os
import igraph as ig
from astart import AStart as BatchAStart

def parse_map(f):
    g = []
    with open(f, 'r') as lines:
        h_done = False
        for l in lines:
            if not h_done:
                if l.startswith('map'): h_done = True
                continue
            g.append(list(l.strip()))
    return g

def run_igraph_comparison():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    # 1. Build Adjacency for BatchAStart
    adj = {}
    edges_list = []
    for y in range(h):
        for x in range(w):
            u_idx = y * w + x
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    adj[(x,y)][(nx,ny)] = 1.0
                    v_idx = ny * w + nx
                    edges_list.append((u_idx, v_idx))
    
    # 2. Build igraph (Standard C-based Dijkstra)
    # igraph uses integer indices for nodes
    ig_graph = ig.Graph(n=w*h, edges=edges_list, directed=False)
            
    # Load Scenarios
    scens = []
    with open(m + '.scen', 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = scens[-10:] # 10 long scenarios
    
    print(f"Comparing AStart (Batch) vs IGraph (C-Dijkstra) on {m}...")
    
    # --- BatchAStart (k=1000) ---
    solver = BatchAStart(adj, heuristic_func='manhattan', use_cpp=True)
    t0 = time.time()
    for s, g in test_set:
        solver.solve(s, g, k=1000)
    batch_time = (time.time() - t0) / len(test_set) * 1000
    
    # --- IGraph (Standard C Dijkstra) ---
    t0 = time.time()
    for s, g in test_set:
        s_idx = s[1] * w + s[0]
        g_idx = g[1] * w + g[0]
        ig_graph.get_shortest_paths(s_idx, to=g_idx, weights=None, output="vpath")
    ig_time = (time.time() - t0) / len(test_set) * 1000
    
    print(f"\nRESULTS:")
    print(f"Our Batch A* (C++): {batch_time:>8.3f} ms")
    print(f"IGraph Dijkstra (C): {ig_time:>8.3f} ms")
    print(f"Speedup vs IGraph  : {ig_time / batch_time:.2f}x")

if __name__ == "__main__":
    run_igraph_comparison()
