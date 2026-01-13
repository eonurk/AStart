import time
import os
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
    if not path: return float('inf')
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        dx, dy = abs(u[0]-v[0]), abs(u[1]-v[1])
        if dx+dy == 2: cost += 1.41421356
        else: cost += 1.0
    return cost

def run_direct_comparison():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    adj = {}
    for y in range(h):
        for x in range(w):
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    if dx != 0 and dy != 0:
                        if grid[y][nx] not in passable or grid[ny][x] not in passable: continue
                        adj[(x,y)][(nx,ny)] = 1.41421356
                    else: adj[(x,y)][(nx,ny)] = 1.0
            
    scen = m + '.scen'
    test_set = []
    with open(scen, 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            test_set.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    
    test_set = test_set[-50:] # 50 long paths
    solver = AStart(adj, heuristic_func='octile', use_cpp=True)
    
    print(f"Comparing 50 paths on {m}...")
    print(f"{'Algorithm':<15} | {'Avg Time':<10} | {'Avg Cost'}")
    print("-" * 45)
    
    # 1. Standard A* Baseline
    t0 = time.time()
    std_costs = []
    for s, g in test_set:
        path = solver.solve_classic(s, g)
        std_costs.append(calculate_path_cost(path))
    t_std = (time.time() - t0) / 50 * 1000
    print(f"{'Standard A*':<15} | {t_std:>7.3f} ms | {sum(std_costs)/50:>7.2f}")
    
    # 2. Batch A* (k=1000)
    t0 = time.time()
    batch_costs = []
    for s, g in test_set:
        path = solver.solve(s, g, k=1000)
        batch_costs.append(calculate_path_cost(path))
    t_batch = (time.time() - t0) / 50 * 1000
    print(f"{'Batch A*':<15} | {t_batch:>7.3f} ms | {sum(batch_costs)/50:>7.2f}")
    
    # Check cost difference
    diff = sum(abs(s - b) for s, b in zip(std_costs, batch_costs))
    print("-" * 45)
    print(f"Total Cost Difference: {diff:.6f}")
    if diff < 0.001:
        print("RESULT: Batch A* found EXACTLY the same optimized paths as Standard A*.")
    else:
        print(f"RESULT: Batch A* cost difference is {diff/sum(std_costs)*100:.4f}%")

if __name__ == "__main__":
    run_direct_comparison()
