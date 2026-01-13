import os
import glob
import time
import csv
from astart import AStart

# Configuration
BENCH_DIR = "benchmarks/movingai"
RESULTS_FILE = "benchmarks/movingai_results_high_k.csv"
TIMEOUT_SEC = 60 

def parse_map(filename):
    grid = []
    width, height = 0, 0
    try:
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
                if len(line) > 0: grid.append(list(line))
    except: return None, 0, 0
    return grid, width, height

def build_graph(grid, width, height):
    adj = {}
    passable_chars = {'.', 'G', 'S', 'T'}
    SQRT2 = 1.41421356
    for y in range(height):
        for x in range(width): adj[(x, y)] = {}
    for y in range(height):
        for x in range(width):
            if y < len(grid) and x < len(grid[y]):
                if grid[y][x] not in passable_chars: continue
            else: continue
            u = (x, y)
            for dx, dy, cost in [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,SQRT2),(-1,1,SQRT2),(1,-1,SQRT2),(1,1,SQRT2)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if ny < len(grid) and nx < len(grid[ny]):
                        if grid[ny][nx] in passable_chars:
                            if dx != 0 and dy != 0: # Strict Diagonal
                                if grid[y][nx] not in passable_chars or grid[ny][x] not in passable_chars: continue
                            adj[u][(nx, ny)] = cost
    return adj

def parse_scenarios(filename):
    scenarios = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith("version"): continue
                parts = line.split()
                if len(parts) < 9: continue
                sx, sy, gx, gy, opt = int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7]), float(parts[8])
                scenarios.append(((sx, sy), (gx, gy), opt))
    except: pass
    return scenarios

def calculate_path_cost(path):
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if abs(u[0]-v[0]) + abs(u[1]-v[1]) == 2: cost += 1.41421356
        else: cost += 1.0
    return cost

def run_suite():
    map_files = sorted(glob.glob(os.path.join(BENCH_DIR, "**", "*.map"), recursive=True))[:10]
    print(f"Running High-K Benchmark on {len(map_files)} maps...")
    
    with open(RESULTS_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Map", "Algorithm", "AvgTime(ms)", "Optimality( %)"])
        
        for map_file in map_files:
            map_name = os.path.basename(map_file)
            scen_file = map_file + ".scen"
            if not os.path.exists(scen_file): scen_file = os.path.splitext(map_file)[0] + ".map.scen"
            if not os.path.exists(scen_file): continue
            
            grid, w, h = parse_map(map_file)
            if not grid: continue
            adj = build_graph(grid, w, h)
            scenarios = sorted(parse_scenarios(scen_file), key=lambda x: x[2], reverse=True)[:10]
            solver = AStart(adj, heuristic_func='octile', use_cpp=True)
            
            print(f"\n{map_name} ({w}x{h}):")
            for name, k, adapt in [("Std",1,0), ("B20",20,0), ("B50",50,0), ("B100",100,0), ("A50",50,1)]:
                total_time, opt_cnt = 0, 0
                for s, g, opt in scenarios:
                    t0 = time.time()
                    path = solver.solve(s, g, k=k, adaptive=bool(adapt))
                    total_time += (time.time() - t0)
                    if path and abs(calculate_path_cost(path) - opt) < 0.5: opt_cnt += 1
                avg_ms = (total_time / len(scenarios)) * 1000
                opt_p = (opt_cnt / len(scenarios)) * 100
                print(f"  {name:<5}: {avg_ms:>7.3f} ms | Opt: {opt_p:>5.1f}%")
                writer.writerow([map_name, name, f"{avg_ms:.4f}", f"{opt_p:.1f}"])

if __name__ == "__main__":
    run_suite()
