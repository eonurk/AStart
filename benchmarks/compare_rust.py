import time
import os
import rustworkx as rx
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

def run_third_party_comparison():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    # 1. Build Adjacency for BatchAStart
    adj = {}
    for y in range(h):
        for x in range(w):
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    adj[(x,y)][(nx,ny)] = 1.0
    
    # 2. Build Rustworkx Graph (Standard A*)
    rx_graph = rx.PyGraph()
    # Add nodes and keep a map
    nodes = {}
    for y in range(h):
        for x in range(w):
            nodes[(x,y)] = rx_graph.add_node((x,y))
    # Add edges
    for u, nbrs in adj.items():
        for v, weight in nbrs.items():
            rx_graph.add_edge(nodes[u], nodes[v], weight)
            
    # Load Scenarios
    scens = []
    with open(m + '.scen', 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = scens[-10:] # 10 long scenarios
    
    print(f"Comparing AStart vs Rustworkx (Rust) on {m}...")
    
    # Heuristic for Rustworkx
    def h_func(u_idx):
        u = rx_graph.get_node_data(u_idx)
        # Goal is fixed per search, but rx.astar expects h(u) -> cost
        # We'll use a hack to pass goal or just use a very simple one for now
        # Actually, rx.astar passes the target node to the heuristic if defined
        return 0 # Baseline: Dijkstra if we can't easily pass goal to the lambda

    # --- BatchAStart (k=1000) ---
    solver = BatchAStart(adj, heuristic_func='manhattan', use_cpp=True)
    t0 = time.time()
    for s, g in test_set:
        solver.solve(s, g, k=1000)
    batch_time = (time.time() - t0) / len(test_set) * 1000
    
    # --- Rustworkx (Standard A*) ---
    t0 = time.time()
    for s, g in test_set:
        # rustworkx.astar(graph, node_a, edge_cost_fn, estimate_cost_fn, node_b)
        rx.astar(rx_graph, nodes[s], lambda x: float(x), 
                 lambda u_idx: abs(rx_graph[u_idx][0]-g[0]) + abs(rx_graph[u_idx][1]-g[1]), 
                 nodes[g])
    rx_time = (time.time() - t0) / len(test_set) * 1000
    
    print(f"\nRESULTS:")
    print(f"Our Batch A* (C++): {batch_time:>8.3f} ms")
    print(f"Rustworkx A* (Rust): {rx_time:>8.3f} ms")
    print(f"Speedup vs Rust   : {rx_time / batch_time:.2f}x")

if __name__ == "__main__":
    run_third_party_comparison()
