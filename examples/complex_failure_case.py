import time
import random
import networkx as nx
from astart import AStart

def run_complex_benchmark():
    print("--- 🌌 Complex Graph Benchmark (Wormholes) 🌌 ---")
    print("Scenario: A* heuristic is inconsistent due to Teleporters.")
    print("Goal: Check if Batch A* finds a better path than Standard A*.\n")

    # 1. Generate 50x50 Grid
    N = 50
    G = nx.grid_2d_graph(N, N)
    
    # Convert to weighted dict
    # Standard grid edges cost 10
    adj = {n: {} for n in G.nodes()}
    for u, v in G.edges():
        adj[u][v] = 10
        adj[v][u] = 10

    nodes = list(G.nodes())
    
    # 2. Add "Wormholes" (The Trap)
    # Connect distant nodes with Cost 1
    # This breaks the Manhattan heuristic (which thinks dist is ~800, but it's 1)
    num_wormholes = 20
    wormholes = []
    rng = random.Random(42) # Fixed seed
    
    for _ in range(num_wormholes):
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v:
            # Only make it a wormhole if they are far apart
            dist = abs(u[0]-v[0]) + abs(u[1]-v[1])
            if dist > 30:
                adj[u][v] = 1
                adj[v][u] = 1 # bidirectional
                wormholes.append((u, v))

    start = (0, 0)
    goal = (N-1, N-1)

    # 3. Heuristics
    # A. Consistent (Dijkstra) - The Ground Truth
    def h_dijkstra(u, g): return 0
    
    # B. Inconsistent (Manhattan) - The "Trap" for A*
    # Assumes cost is 10 per step (grid), so h = dist * 10
    def h_manhattan(u, g):
        return (abs(u[0]-g[0]) + abs(u[1]-g[1])) * 10

    # --- Run 1: Ground Truth (Dijkstra) ---
    print(f"1. Running Ground Truth (Dijkstra)...")
    solver_true = AStart(adj, h_dijkstra)
    path_true = solver_true.solve(start, goal, k=1)
    cost_true = calculate_cost(adj, path_true)
    print(f"   -> True Optimal Cost: {cost_true}\n")

    # --- Run 2: Standard A* (k=1) with Inconsistent Heuristic ---
    print(f"2. Running Standard A* (k=1) with Inconsistent Heuristic...")
    solver_std = AStart(adj, h_manhattan)
    path_std = solver_std.solve(start, goal, k=1)
    cost_std = calculate_cost(adj, path_std)
    print(f"   -> Found Cost: {cost_std}")
    if cost_std > cost_true:
        print(f"   ❌ FAILED! Suboptimal by {cost_std - cost_true}")
    else:
        print(f"   ✅ Optimal")

    # --- Run 3: Batch A* (k=15) with Inconsistent Heuristic ---
    print(f"\n3. Running Batch A* (k=15) with Inconsistent Heuristic...")
    solver_batch = AStart(adj, h_manhattan)
    path_batch = solver_batch.solve(start, goal, k=15)
    cost_batch = calculate_cost(adj, path_batch)
    print(f"   -> Found Cost: {cost_batch}")
    
    diff = cost_std - cost_batch
    if cost_batch < cost_std:
        print(f"   ✅ Batch A* performed BETTER! Saved {diff} cost.")
        if cost_batch == cost_true:
            print(f"   🚀 Batch A* found the OPTIMAL path despite the bad heuristic!")
    elif cost_batch > cost_true:
        print(f"   ⚠️  Batch A* also failed (Cost {cost_batch}).")
    else:
        print(f"   😐 No improvement.")

def calculate_cost(graph, path):
    if not path: return float('inf')
    cost = 0
    for i in range(len(path)-1):
        cost += graph[path[i]][path[i+1]]
    return cost

if __name__ == "__main__":
    run_complex_benchmark()
