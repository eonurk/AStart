import os
import time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from astart import AStart

# Load a medium map
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

def build_scipy_graph(grid, w, h):
    # Map nodes to indices
    num_nodes = w * h
    row = []
    col = []
    data = []
    passable = {'.', 'G', 'S', 'T'}
    
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in passable: continue
            u = y * w + x
            for dx, dy, c in [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    v = ny * w + nx
                    row.append(u)
                    col.append(v)
                    data.append(float(c))
    return csr_matrix((data, (row, col)), shape=(num_nodes, num_nodes))

def build_astart_graph(grid, w, h):
    adj = {}
    passable = {'.', 'G', 'S', 'T'}
    for y in range(h):
        for x in range(w):
            adj[(x,y)] = {}
            if grid[y][x] not in passable: continue
            for dx, dy, c in [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in passable:
                    adj[(x,y)][(nx,ny)] = float(c)
    return adj

def run_comparison():
    mname = "den012d.map"
    path = f"benchmarks/movingai/dao/{mname}"
    grid, w, h = parse_map(path)
    
    print(f"Building Graphs for {mname} ({w}x{h})...")
    adj = build_astart_graph(grid, w, h)
    csr = build_scipy_graph(grid, w, h)
    
    # 5 long paths from scenario
    scens = []
    with open(path + ".scen", 'r') as f:
        for line in f:
            if line.startswith("version"): continue
            p = line.split()
            scens.append(((int(p[4]), int(p[5])), (int(p[6]), int(p[7]))))
    test_set = scens[-5:] # Take 5 long ones
    
    # AStart (k=1000)
    solver = AStart(adj, heuristic_func='manhattan', use_cpp=True)
    t0 = time.time()
    for s, g in test_set:
        solver.solve(s, g, k=1000)
    astart_time = (time.time() - t0) / 5 * 1000
    
    # Scipy Dijkstra
    t0 = time.time()
    for s, g in test_set:
        start_idx = s[1] * w + s[0]
        goal_idx = g[1] * w + g[0]
        # Dijkstra returns full dist matrix or path
        dijkstra(csr, directed=False, indices=start_idx, return_predecessors=False)
    scipy_time = (time.time() - t0) / 5 * 1000
    
    print(f"\nRESULTS (Avg Time per Path):")
    print(f"AStart (Batch-1000): {astart_time:>7.3f} ms")
    print(f"Scipy (Dijkstra)   : {scipy_time:>7.3f} ms")
    print(f"Speedup vs Scipy   : {scipy_time / astart_time:.2f}x")

if __name__ == "__main__":
    run_comparison()
