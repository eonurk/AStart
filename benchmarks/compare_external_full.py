import os
import time
import numpy as np
from skimage.graph import route_through_array
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from astart import AStart as BatchAStart

def parse_map(filename):
    grid = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        header_done = False
        for line in lines:
            line = line.strip()
            if not header_done:
                if line.startswith("height"): h = int(line.split()[1])
                elif line.startswith("width"): w = int(line.split()[1])
                elif line.startswith("map"): header_done = True
                continue
            if line: grid.append(list(line))
    return grid, w, h

def run_comparison():
    mname = "den012d.map"
    path = f"benchmarks/movingai/dao/{mname}"
    grid_raw, w, h = parse_map(path)
    passable = {'.', 'G', 'S', 'T'}
    
    # 1. Prepare data for BatchAStart (C++)
    adj = {}
    for y in range(h):
        for x in range(w):
            adj[(x,y)] = {}
            if grid_raw[y][x] not in passable: continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid_raw[ny][nx] in passable:
                    adj[(x,y)][(nx,ny)] = 1.0
    
    # 2. Prepare data for Scikit-Image (C-based array)
    # MCP needs a cost array where walls are very high cost
    cost_grid = np.ones((h, w), dtype=np.float32)
    for y in range(h):
        for x in range(w):
            if grid_raw[y][x] not in passable:
                cost_grid[y][x] = 1e6 # "Wall"
    
    # 3. Prepare data for Python-Pathfinding
    pf_matrix = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(1 if grid_raw[y][x] in passable else 0)
        pf_matrix.append(row)
    
    # Scenarios
    scens = []
    with open(path + ".scen", 'r') as f:
        for line in f:
            if line.startswith("version"): continue
            p = line.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = scens[-5:] # 5 long paths
    
    print(f"Comparing A* Implementations on {mname} ({w}x{h}):")
    
    # --- BatchAStart (k=1000) ---
    solver = BatchAStart(adj, heuristic_func='manhattan', use_cpp=True)
    t0 = time.time()
    for s, g in test_set:
        solver.solve(s, g, k=1000)
    batch_time = (time.time() - t0) / 5 * 1000
    
    # --- Scikit-Image (C-based) ---
    t0 = time.time()
    for s, g in test_set:
        # route_through_array(array, start, end, fully_connected=False)
        route_through_array(cost_grid, [s[1], s[0]], [g[1], g[0]], fully_connected=False)
    sk_time = (time.time() - t0) / 5 * 1000
    
    # --- Python-Pathfinding (Standard A*) ---
    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    t0 = time.time()
    for s, g in test_set:
        pf_grid = Grid(matrix=pf_matrix)
        start_node = pf_grid.node(s[0], s[1])
        end_node = pf_grid.node(g[0], g[1])
        finder.find_path(start_node, end_node, pf_grid)
    pf_time = (time.time() - t0) / 5 * 1000
    
    print(f"\nRESULTS (Avg Time per Path):")
    print(f"1. Our Batch A* (k=1000) : {batch_time:>8.3f} ms")
    print(f"2. Scikit-Image (C-A*)    : {sk_time:>8.3f} ms")
    print(f"3. Pathfinding (Python A*): {pf_time:>8.3f} ms")
    print("-" * 40)
    print(f"Speedup vs C-based A*    : {sk_time / batch_time:.2f}x")
    print(f"Speedup vs Python A*     : {pf_time / batch_time:.2f}x")

if __name__ == "__main__":
    run_comparison()
