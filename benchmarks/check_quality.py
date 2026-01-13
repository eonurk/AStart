import os
import glob
import time
from astart import AStart

# Configuration
BENCH_DIR = "benchmarks/movingai"

def parse_map(filename):
    grid = []
    width, height = 0, 0
    with open(filename, 'r') as f:
        lines = f.readlines()
        header_done = False
        for line in lines:
            line = line.strip()
            if not header_done:
                if line.startswith("height"): height = int(line.split()[1])
                elif line.startswith("width"): width = int(line.split()[1])
                elif line.startswith("map"): header_done = True
                continue
            if line: grid.append(list(line))
    return grid, width, height

def build_graph(grid, width, height):
    adj = {}
    passable = {'.', 'G', 'S', 'T'}
    SQRT2 = 1.41421356
    
    # CRITICAL: Include ALL nodes to keep row-major mapping correct for C++
    for y in range(height):
        for x in range(width):
            adj[(x,y)] = {}
            
    for y in range(height):
        for x in range(width):
            if y >= len(grid) or x >= len(grid[y]) or grid[y][x] not in passable: continue
            u = (x,y)
            for dx, dy, c in [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,SQRT2),(-1,1,SQRT2),(1,-1,SQRT2),(1,1,SQRT2)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height and ny < len(grid) and nx < len(grid[ny]) and grid[ny][nx] in passable:
                    if dx != 0 and dy != 0: 
                        if grid[y][nx] not in passable or grid[ny][x] not in passable: continue
                    adj[u][(nx,ny)] = c
    return adj

def calculate_path_cost(path):
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if abs(u[0]-v[0]) + abs(u[1]-v[1]) == 2: cost += 1.41421356
        else: cost += 1.0
    return cost

def run_quality_check():
    mname = "den012d.map"
    path = os.path.join(BENCH_DIR, "dao", mname)
    grid, w, h = parse_map(path)
    adj = build_graph(grid, w, h)
    scen_path = path + ".scen"
    
    with open(scen_path, 'r') as f:
        scens = []
        for line in f:
            if line.startswith("version"): continue
            p = line.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7])), float(p[8])))
    
    # Take 5 long paths
    scens.sort(key=lambda x: x[2], reverse=True)
    test_set = scens[:5]
    
    solver = AStart(adj, heuristic_func='octile', use_cpp=True)
    
    print(f"QUALITY CHECK: {mname}")
    print(f"{'K':<10} | {'AVG TIME':<10} | {'AVG COST OVERHEAD'}")
    print("-" * 45)
    
    # Get baseline cost
    base_costs = []
    for s, g, opt in test_set:
        p = solver.solve(s, g, k=1)
        base_costs.append(calculate_path_cost(p))
    
    for k in [1, 20, 100, 500]:
        total_time = 0
        total_overhead = 0
        for i, (s, g, opt) in enumerate(test_set):
            t0 = time.time()
            path = solver.solve(s, g, k=k)
            total_time += (time.time() - t0)
            
            cost = calculate_path_cost(path)
            overhead = cost - base_costs[i]
            total_overhead += overhead
            # print(f"DEBUG: k={k}, path_len={len(path)}, cost={cost:.2f}, base={base_costs[i]:.2f}")
            
        avg_ms = (total_time / len(test_set)) * 1000
        avg_over = total_overhead / len(test_set)
        print(f"{k:<10} | {avg_ms:>7.3f} ms | {avg_over:>7.3f} units (Base: {sum(base_costs)/len(base_costs):.1f})")

if __name__ == "__main__":
    run_quality_check()
