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

def calculate_path_cost(path):
    if not path: return float('inf')
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        dx = abs(u[0] - v[0])
        dy = abs(u[1] - v[1])
        if dx + dy == 2: cost += 1.41421356
        else: cost += 1.0
    return cost

def run_precision_test():
    m = 'benchmarks/movingai/dao/den012d.map'
    grid = parse_map(m)
    h, w = len(grid), len(grid[0])
    passable = {'.', 'G', 'S', 'T'}
    
    # Build Graph
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
            
    scens = []
    with open(m + '.scen', 'r') as f:
        for l in f:
            if l.startswith('version'): continue
            p = l.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7])), float(p[8])))
    test_set = scens[-20:] # 20 long scenarios
    
    solver = BatchAStart(adj, heuristic_func='octile', use_cpp=True)
    
    print(f"{'K':<10} | {'AVG TIME':<10} | {'AVG COST':<10} | {'OPTIMALITY'}")
    print("-" * 50)
    
    for k in [1, 20, 100, 1000]:
        total_time = 0
        total_cost = 0
        optimal_matches = 0
        
        for s, g, opt in test_set:
            t0 = time.time()
            path = solver.solve(s, g, k=k)
            total_time += (time.time() - t0)
            
            cost = calculate_path_cost(path)
            total_cost += cost
            if abs(cost - opt) < 0.5: # Allow small float margin
                optimal_matches += 1
                
        avg_ms = (total_time / len(test_set)) * 1000
        avg_cost = total_cost / len(test_set)
        opt_rate = (optimal_matches / len(test_set)) * 100
        print(f"{k:<10} | {avg_ms:>7.3f} ms | {avg_cost:>7.2f} | {opt_rate:>5.1f}%")

if __name__ == "__main__":
    run_precision_test()
