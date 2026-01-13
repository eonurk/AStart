import os
import glob
import time
import csv
from astart import AStart

# Configuration
BENCH_DIR = "benchmarks/movingai"
RESULTS_FILE = "benchmarks/movingai_results.csv"
TIMEOUT_SEC = 60  # Skip map if building graph takes too long

def parse_map(filename):
    grid = []
    width = 0
    height = 0
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            header_done = False
            for line in lines:
                line = line.strip()
                if not header_done:
                    if line.startswith("height"):
                        height = int(line.split()[1])
                    elif line.startswith("width"):
                        width = int(line.split()[1])
                    elif line.startswith("map"):
                        header_done = True
                    continue
                if len(line) > 0:
                    grid.append(list(line))
    except Exception as e:
        print(f"Error parsing map {filename}: {e}")
        return None, 0, 0
    return grid, width, height

def build_graph(grid, width, height):
    adj = {}
    passable_chars = {'.', 'G', 'S', 'T'} # T = Trees, etc.
    SQRT2 = 1.41421356
    
    # Pre-allocate
    for y in range(height):
        for x in range(width):
            adj[(x, y)] = {}
            
    for y in range(height):
        for x in range(width):
            if y < len(grid) and x < len(grid[y]):
                if grid[y][x] not in passable_chars: continue
            else: continue
            
            u = (x, y)
            
            # 8-Connected Neighbors (Octile)
            # Order: Cardinals then Diagonals
            moves = [
                (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
                (-1, -1, SQRT2), (-1, 1, SQRT2), (1, -1, SQRT2), (1, 1, SQRT2)
            ]
            
            for dx, dy, cost in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if ny < len(grid) and nx < len(grid[ny]):
                        if grid[ny][nx] in passable_chars:
                            # Strict Diagonal Check (No Corner Cutting)
                            if dx != 0 and dy != 0:
                                # Check cardinals
                                # (x+dx, y) and (x, y+dy) must be passable
                                if grid[y][nx] not in passable_chars or grid[ny][x] not in passable_chars:
                                    continue
                            
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
                sx, sy = int(parts[4]), int(parts[5])
                gx, gy = int(parts[6]), int(parts[7])
                opt = float(parts[8])
                scenarios.append(((sx, sy), (gx, gy), opt))
    except:
        pass
    return scenarios

def calculate_path_cost(path):
    cost = 0.0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        dx = abs(u[0] - v[0])
        dy = abs(u[1] - v[1])
        if dx + dy == 2: # Diagonal
            cost += 1.41421356
        else:
            cost += 1.0
    return cost

def run_suite():

    map_files = glob.glob(os.path.join(BENCH_DIR, "**", "*.map"), recursive=True)

    # Sort to be deterministic

    map_files.sort()

    # Take a subset for a quick stress test of high K

    map_files = map_files[:20]

    print(f"Found {len(map_files)} maps for High-K test.")

    

    with open(RESULTS_FILE, 'w', newline='') as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(["Map", "Scenarios", "Algorithm", "TotalTime(s)", "AvgTime(ms)", "Optimality(%)"])

        

        for map_file in map_files:

            # ... (loading logic)

            # (I'll skip the repetition and just update the modes)

            

            modes = [

                ("Standard A* (k=1)", 1, False),

                ("Batch A* (k=20)", 20, False),

                ("Batch A* (k=50)", 50, False),

                ("Batch A* (k=100)", 100, False),

                ("Adaptive A* (k=50)", 50, True)

            ]
            
            for algo_name, k, adapt in modes:
                total_time = 0
                optimal_cnt = 0
                
                for start, goal, opt_len in scenarios:
                    t_start = time.time()
                    path = solver.solve(start, goal, k=k, adaptive=adapt)
                    total_time += (time.time() - t_start)
                    
                    if path:
                        cost = calculate_path_cost(path)
                        # Check optimality with epsilon
                        if abs(cost - opt_len) < 0.001 * opt_len: # 0.1% tolerance
                            optimal_cnt += 1
                        elif abs(cost - opt_len) < 0.5: # Absolute tolerance
                             optimal_cnt += 1
                
                avg_time = (total_time / len(scenarios)) * 1000
                optimality = (optimal_cnt / len(scenarios)) * 100
                
                print(f"    {algo_name:<20}: {avg_time:.3f} ms/path | Opt: {optimality:.1f}%")
                writer.writerow([map_name, len(scenarios), algo_name, f"{total_time:.4f}", f"{avg_time:.4f}", f"{optimality:.1f}"])
                csvfile.flush()

if __name__ == "__main__":
    run_suite()
