import time
import os
import networkit as nk
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

def run_networkit_comparison():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    nk_graph = nk.Graph(w * h, weighted=True, directed=False)
    adj = {}
    for y in range(h):
        for x in range(w):
            u_idx = y * w + x
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    v_idx = ny * w + nx
                    nk_graph.addEdge(u_idx, v_idx, 1.0)
                    adj[(x,y)][(nx,ny)] = 1.0
            
    scens = []
    with open(m + '.scen', 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = scens[-10:]
    
    print(f"Comparing AStart (Batch) vs NetworKit (C++ A*) on {m}...")
    
    # --- BatchAStart (k=1000) ---
    solver = BatchAStart(adj, heuristic_func='manhattan', use_cpp=True)
    t0 = time.time()
    for s, g in test_set:
        solver.solve(s, g, k=1000)
    batch_time = (time.time() - t0) / len(test_set) * 1000
    
    # --- NetworKit A* (C++) ---
    t0 = time.time()
    for s, g in test_set:
        s_idx = s[1] * w + s[0]
        g_idx = g[1] * w + g[0]
        gx, gy = g_idx % w, g_idx // w
        
        # Pre-calculate heuristic vector (required by NetworKit)
        # To be fair, we include this in the timing
        h_vals = [float(abs(i%w - gx) + abs(i//w - gy)) for i in range(w*h)]
            
        nk_astar = nk.distance.AStar(nk_graph, h_vals, s_idx, g_idx)
        nk_astar.run()
        nk_astar.getPath()
        
    nk_time = (time.time() - t0) / len(test_set) * 1000
    
    print(f"\nRESULTS:")
    print(f"Our Batch A* (C++): {batch_time:>8.3f} ms")
    print(f"NetworKit A* (C++) : {nk_time:>8.3f} ms")
    print(f"Speedup vs NetworKit: {nk_time / batch_time:.2f}x")

if __name__ == "__main__":
    run_networkit_comparison()