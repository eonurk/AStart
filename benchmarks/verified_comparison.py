import time
import os
import glob
import ctypes
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

def build_graph(grid):
    h, w = len(grid), len(grid[0])
    adj = {}
    for y in range(h):
        for x in range(w):
            adj[(x,y)] = {}
            if grid[y][x] not in '.GST': continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in '.GST':
                    if dx != 0 and dy != 0:
                        if grid[y][nx] not in '.GST' or grid[ny][x] not in '.GST': continue
                        adj[(x,y)][(nx,ny)] = 1.41421356
                    else: adj[(x,y)][(nx,ny)] = 1.0
    return adj

def run_verified_benchmark():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    adj = build_graph(grid)
    
    scen = m + '.scen'
    test_set = []
    with open(scen, 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            test_set.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    
    test_set = test_set[-50:] # 50 scenarios
    
    print("Initializing AStart...")
    # The AStart class will find the .so if it's in the build/ folder or installed
    # Let's ensure we find it.
    try:
        s = AStart(adj, heuristic_func='octile', use_cpp=True)
    except Exception as e:
        print(f"FAILED TO INIT: {e}")
        return

    # 1. VERIFICATION
    print("Verifying correctness...")
    p1 = s.solve_classic(test_set[0][0], test_set[0][1])
    p2 = s.solve(test_set[0][0], test_set[0][1], k=500)
    
    if p1 is None or p2 is None:
        print(f"ERROR: No path found! p1={p1 is not None}, p2={p2 is not None}")
        return
    
    print(f"Paths Found! Lengths: Classic={len(p1)}, Batch={len(p2)}")
    
    # 2. TIMING
    print("\nStarting timing benchmark...")
    t0 = time.time()
    for st, g in test_set:
        s.solve_classic(st, g)
    t_std = (time.time() - t0) / len(test_set) * 1000
    
    t0 = time.time()
    for st, g in test_set:
        s.solve(st, g, k=500)
    t_batch = (time.time() - t0) / len(test_set) * 1000
    
    print(f"\nRESULTS:")
    print(f"Classic A* (C++): {t_std:.3f} ms")
    print(f"Batch   A* (C++): {t_batch:.3f} ms")
    print(f"Speedup         : {t_std/t_batch:.2f}x")

if __name__ == "__main__":
    run_verified_benchmark()
