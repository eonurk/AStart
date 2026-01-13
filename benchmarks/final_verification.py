import time
import os
import glob
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

def run_final_aggregate():
    map_files = sorted(glob.glob("benchmarks/movingai/dao/*.map"))
    # Pick every 8th map to get a diverse spread of 20 maps
    test_maps = map_files[::8]
    
    print(f"Starting Final Aggregate Benchmark on {len(test_maps)} maps for 3 algorithms...")
    
    stats = {"Std": [], "NK": [], "Batch": [], "Costs": []}
    
    for m_path in test_maps:
        mname = os.path.basename(m_path)
        grid = parse_map(m_path)
        h, w = len(grid), len(grid[0])
        passable = {'.', 'G', 'S', 'T'}
        
        # Build Graphs
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
                        cost = 1.41421356 if (dx != 0 and dy != 0) else 1.0
                        if dx != 0 and dy != 0:
                            if grid[y][nx] not in passable or grid[ny][x] not in passable: continue
                        adj[(x,y)][(nx,ny)] = cost
                        nk_graph.addEdge(u_idx, ny * w + nx, cost)
        
        scen = m_path + '.scen'
        test_set = []
        with open(scen, 'r') as f:
            for l in f:
                if l.startswith('version'): continue
                p = l.split()
                test_set.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
        test_set = test_set[-10:] # 10 scenarios per map
        
        solver = AStart(adj, heuristic_func='octile', use_cpp=True)
        
        # 1. Standard A*
        t0 = time.time()
        std_costs = []
        for s, g in test_set:
            p = solver.solve_classic(s, g)
            std_costs.append(calculate_path_cost(p))
        stats["Std"].append((time.time()-t0)/10*1000)
        
        # 2. NetworKit
        t0 = time.time()
        for s, g in test_set:
            s_idx, g_idx = s[1]*w+s[0], g[1]*w+g[0]
            # Fast heuristic vector pre-calc
            gx, gy = g[0], g[1]
            h_vals = [float(abs(i%w - gx) + abs(i//w - gy)) for i in range(w*h)]
            nk_astar = nk.distance.AStar(nk_graph, h_vals, s_idx, g_idx)
            nk_astar.run()
        stats["NK"].append((time.time()-t0)/10*1000)
        
        # 3. Batch A* (k=1000)
        t0 = time.time()
        batch_costs = []
        for s, g in test_set:
            p = solver.solve(s, g, k=1000)
            batch_costs.append(calculate_path_cost(p))
        stats["Batch"].append((time.time()-t0)/10*1000)
        
        # Track overhead
        for sc, bc in zip(std_costs, batch_costs):
            if sc > 0: stats["Costs"].append(bc / sc)

        print(f"  Done: {mname} ({w}x{h})")

    avg_std = sum(stats["Std"]) / len(test_maps)
    avg_nk = sum(stats["NK"]) / len(test_maps)
    avg_batch = sum(stats["Batch"]) / len(test_maps)
    avg_overhead = (sum(stats["Costs"]) / len(stats["Costs"]) - 1) * 100
    
    print("\nFINAL AGGREGATE RESULTS:")
    print(f"| Algorithm | Avg Time | Speedup | Overhead |")
    print(f"| :--- | :--- | :--- | :--- |")
    print(f"| Standard A* | {avg_std:.3f} ms | 1.00x | 0.00% |")
    print(f"| NetworKit   | {avg_nk:.3f} ms | {avg_std/avg_nk:.2f}x | 0.00% |")
    print(f"| **Batch-1000** | **{avg_batch:.3f} ms** | **{avg_std/avg_batch:.2f}x** | **{avg_overhead:.4f}%** |")

if __name__ == "__main__":
    run_final_aggregate()
