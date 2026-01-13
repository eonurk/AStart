import time
import heapq
from collections import defaultdict
from astart import AStart

# Create a simple graph (Line) to force expansions
# A -> B -> C ... -> Goal
N = 100
graph = {i: {i+1: 1} for i in range(N-1)}
graph[N-1] = {}

# Expensive Heuristic
def expensive_h(u, goal):
    # Simulate work (e.g., 0.1ms per call)
    start = time.time()
    while time.time() - start < 0.0001:
        pass 
    return 0

print(f"Running Standard A* with expensive heuristic...")
solver = AStart(graph, expensive_h)
t0 = time.time()
solver.solve(0, N-1, k=1)
print(f"Standard Time: {time.time() - t0:.4f}s")
print(f"Heuristic Calls (approx): {solver.stats['heap_pushes']}") 

print(f"\nRunning Batch A* (k=10) with expensive heuristic...")
solver = AStart(graph, expensive_h)
t0 = time.time()
solver.solve(0, N-1, k=10)
print(f"Batch Time:    {time.time() - t0:.4f}s")
print(f"Heuristic Calls (approx): {solver.stats['heap_pushes']}")
