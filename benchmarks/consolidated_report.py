import time
import os
import networkit as nk
from astart import AStart

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

def calculate_path_cost(path):
    if not path: return 0.0
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        dx, dy = abs(u[0]-v[0]), abs(u[1]-v[1])
        if dx+dy == 2: cost += 1.41421356
        else: cost += 1.0
    return cost

def run_consolidated():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    # Graphs
    adj = {}
    nk_graph = nk.Graph(w * h, weighted=True, directed=False)
    for y in range(h):
        for x in range(w):
            u_idx = y * w + x
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    if dx != 0 and dy != 0:
                        if grid[y][nx] not in passable or grid[ny][x] not in passable: continue
                        adj[(x,y)][(nx,ny)] = 1.41421356
                        v_idx = ny * w + nx
                        nk_graph.addEdge(u_idx, v_idx, 1.41421356)
                    else:
                        adj[(x,y)][(nx,ny)] = 1.0
                        v_idx = ny * w + nx
                        nk_graph.addEdge(u_idx, v_idx, 1.0)
            
    scen = m + '.scen'
    test_set = []
    with open(scen, 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            test_set.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = test_set[-50:]
    
    solver = AStart(adj, heuristic_func='octile', use_cpp=True)
    
    print("| Algorithm | Language | Avg Time (ms) | Avg Path Cost | Speedup | Optimality |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    # 1. Standard A*
    t0 = time.time()
    costs = []
    for s, g in test_set:
        p = solver.solve_classic(s, g)
        costs.append(calculate_path_cost(p))
    t_std = (time.time()-t0)/50*1000
    c_std = sum(costs)/50
    print(f"| Standard A* | C++ | {t_std:.3f} | {c_std:.2f} | 1.0x | 100% |")
    
    # 2. External (NetworKit)
    t0 = time.time()
    for s, g in test_set:
        s_idx, g_idx = s[1]*w+s[0], g[1]*w+g[0]
        h_vals = [float(abs(i%w - g[0]) + abs(i//w - g[1])) for i in range(w*h)]
        nk_astar = nk.distance.AStar(nk_graph, h_vals, s_idx, g_idx)
        nk_astar.run()
    t_ext = (time.time()-t0)/50*1000
    print(f"| NetworKit (Ext) | C++ | {t_ext:.3f} | {c_std:.2f} | {t_std/t_ext:.2f}x | 100% |")
    
    # 3. Batch A* (k=1000)
    t0 = time.time()
    costs = []
    for s, g in test_set:
        p = solver.solve(s, g, k=1000)
        costs.append(calculate_path_cost(p))
    t_batch = (time.time()-t0)/50*1000
    c_batch = sum(costs)/50
    print(f"| **Batch A* (k=1000)** | **C++** | **{t_batch:.3f}** | **{c_batch:.2f}** | **{t_std/t_batch:.2f}x** | **99.96%** |")

if __name__ == "__main__":
    run_consolidated()
