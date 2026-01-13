import time
import networkx as nx
import random
from astart import AStart

def run_comparison():
    # 1. Generate a "Dense-ish" Graph (where this algo shines)
    print("Generating Graph (Grid with random shortcuts)...")
    N = 50
    # A Grid Graph is good for visualization, but standard A* is already very fast on it.
    # We add random shortcuts to increase connectivity (density).
    G = nx.grid_2d_graph(N, N)
    nodes = list(G.nodes())
    
    # Convert to dict of dicts with weights
    adj = {n: {} for n in G.nodes()}
    for u, v in G.edges():
        w = random.randint(1, 10)
        adj[u][v] = w
        adj[v][u] = w # Undirected for simplicity
        
    # Add random long-range shortcuts to simulate a complex network
    for _ in range(N * 5):
        u, v = random.sample(nodes, 2)
        adj[u][v] = random.randint(1, 50)
        adj[v][u] = random.randint(1, 50)

    start = (0, 0)
    goal = (N-1, N-1)

    # Heuristic
    # NOTE: Using h=0 (Dijkstra) because random shortcuts with low weights 
    # make Manhattan distance inconsistent (h(u) > c(u,v) + h(v)).
    # Consistent heuristic is required for A* with Closed Set to be optimal.
    def h(u, goal):
        return 0

    def calculate_cost(graph_adj, path):
        if not path: return float('inf')
        cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            cost += graph_adj[u][v]
        return cost

    # --- Run Standard A* (k=1) ---
    print(f"\nRunning Standard A* (Simulated by k=1)...")
    solver_std = AStart(adj, h)
    t0 = time.time()
    path_std = solver_std.solve(start, goal, k=1)
    t1 = time.time()
    
    cost_std = calculate_cost(adj, path_std)
    print(f"Time: {t1-t0:.4f}s")
    print(f"Path Length (Steps): {len(path_std) if path_std else 'None'}")
    print(f"Total Weighted Cost: {cost_std}")
    print(f"Stats: {solver_std.stats}")

    # --- Run Batch A* (k=10) ---
    print(f"\nRunning Batch A* (Frontier Reduction k=10)...")
    solver_batch = AStart(adj, h)
    t0 = time.time()
    path_batch = solver_batch.solve(start, goal, k=10)
    t1 = time.time()

    cost_batch = calculate_cost(adj, path_batch)
    print(f"Time: {t1-t0:.4f}s")
    print(f"Path Length (Steps): {len(path_batch) if path_batch else 'None'}")
    print(f"Total Weighted Cost: {cost_batch}")
    print(f"Stats: {solver_batch.stats}")
    
    # Comparison
    pushes_std = solver_std.stats['heap_pushes']
    pushes_batch = solver_batch.stats['heap_pushes']
    print(f"\n--- Reduction ---")
    print(f"Heap Pushes Reduced by: {pushes_std / max(1, pushes_batch):.2f}x")
    if cost_std == cost_batch:
        print("SUCCESS: Optimal costs match.")
    else:
        print(f"WARNING: Costs differ! Standard: {cost_std}, Batch: {cost_batch}")

if __name__ == "__main__":
    run_comparison()