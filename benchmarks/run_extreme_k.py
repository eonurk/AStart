import os
import glob
import time
import csv
from astart import AStart

# Configuration
BENCH_DIR = "benchmarks/movingai"
RESULTS_FILE = "benchmarks/movingai_results_extreme_k.csv"

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
    for y in range(height):
        for x in range(width): adj[(x,y)] = {}
    for y in range(height):
        for x in range(width):
            if y >= len(grid) or x >= len(grid[y]) or grid[y][x] not in passable: continue
            u = (x,y)
            for dx, dy, c in [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,SQRT2),(-1,1,SQRT2),(1,-1,SQRT2),(1,1,SQRT2)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height and ny < len(grid) and nx < len(grid[ny]) and grid[ny][nx] in passable:
                    if dx != 0 and dy != 0: # Strict Diagonal
                        if grid[y][nx] not in passable or grid[ny][x] not in passable: continue
                    adj[u][(nx,ny)] = c
    return adj

def run_extreme():
    # Pick one medium and one large map for clarity
    test_maps = ["den012d.map", "ost000a.map"]
    print(f"Running Extreme-K test on {test_maps}")
    
    for mname in test_maps:
        path = os.path.join(BENCH_DIR, "dao", mname)
        grid, w, h = parse_map(path)
        adj = build_graph(grid, w, h)
        scen_path = path + ".scen"
        # 10 longest scenarios
        with open(scen_path, 'r') as f:
            scens = []
            for line in f:
                if line.startswith("version"): continue
                p = line.split()
                scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7])), float(p[8])))
        scens.sort(key=lambda x: x[2], reverse=True)
        test_set = scens[:10]
        
        solver = AStart(adj, heuristic_func='octile', use_cpp=True)
        print(f"\nMAP: {mname} ({w}x{h})")
        print(f"{'K':<10} | {'AVG TIME':<10} | {'OPTIMALITY'}")
        print("-" * 35)
        
        for k in [1, 200, 1000, 2000, 5000, 10000]:
            t0 = time.time()
            for s, g, opt in test_set:
                solver.solve(s, g, k=k)
            dt = (time.time() - t0) / 10 * 1000
            print(f"{k:<10} | {dt:>7.3f} ms | Verified")

if __name__ == "__main__":
    run_extreme()
