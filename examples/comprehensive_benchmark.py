import time
import networkx as nx
import random
from astart import AStart
import sys

# --- Configuration ---
N = 100  # Grid Size (100x100 = 10,000 nodes)
K = 20   # Batch size

def manhattan(u, goal):
    return abs(u[0] - goal[0]) + abs(u[1] - goal[1])

# --- Graph Generators ---

def gen_open_grid(n):
    """Mostly open grid with some random obstacles."""
    G = nx.grid_2d_graph(n, n)
    nodes = list(G.nodes())
    # Remove 10% random nodes
    to_remove = random.sample(nodes, int(n*n*0.1))
    G.remove_nodes_from(to_remove)
    return G

def gen_maze(n):
    """Perfect maze using MST (lots of dead ends)."""
    # Create full grid
    G = nx.grid_2d_graph(n, n)
    # Assign random weights
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    # MST creates a maze
    mst = nx.minimum_spanning_tree(G)
    # Add back 5% edges to create some cycles (braided maze) so it's not trivial
    all_edges = list(G.edges())
    random.shuffle(all_edges)
    num_add = int(len(all_edges) * 0.05)
    mst.add_edges_from(all_edges[:num_add])
    return mst

def gen_trap(n):
    """Big U-shaped trap in the middle."""
    G = nx.grid_2d_graph(n, n)
    wall_x = n // 2
    for y in range(n):
        if y < n - 5: # Leave gap at top
            if G.has_node((wall_x, y)):
                G.remove_node((wall_x, y))
    return G

def nx_to_dict(G):
    adj = {}
    for n in G.nodes():
        adj[n] = {}
        for nbr in G.neighbors(n):
            adj[n][nbr] = 1 # Uniform cost
    return adj

# --- Benchmarking Logic ---

def run_suite():
    scenarios = [
        ("Open Field", gen_open_grid),
        ("Maze (Complex)", gen_maze),
        ("Trap (U-Shape)", gen_trap)
    ]

    print(f"{'SCENARIO':<15} | {'ALGORITHM':<25} | {'TIME (s)':<10} | {'PATH LEN':<8} | {'STATUS'}")
    print("-" * 75)

    for name, gen_func in scenarios:
        # Generate Graph
        G = gen_func(N)
        adj = nx_to_dict(G)
        
        # Pick valid Start/Goal
        nodes = list(G.nodes())
        start = (0, 0) if (0,0) in G else nodes[0]
        goal = (N-1, N-1) if (N-1, N-1) in G else nodes[-1]
        
        # Ensure path exists
        if not nx.has_path(G, start, goal):
            print(f"{name:<15} | SKIPPED (No Path)")
            continue

        # 1. NetworkX A* (Baseline)
        t0 = time.time()
        try:
            nx_path = nx.astar_path(G, start, goal, heuristic=manhattan)
            nx_time = time.time() - t0
            print(f"{name:<15} | {'NetworkX A*':<25} | {nx_time:<10.5f} | {len(nx_path):<8} | Baseline")
        except:
            print(f"{name:<15} | {'NetworkX A*':<25} | ERROR")

        # 2. AStart (Python Fixed)
        solver_py = AStart(adj, heuristic_func=manhattan, use_cpp=False)
        t0 = time.time()
        path = solver_py.solve(start, goal, k=K, adaptive=False)
        t_py_fixed = time.time() - t0
        print(f"{name:<15} | {'Py Batch A* (Fixed)':<25} | {t_py_fixed:<10.5f} | {len(path) if path else 0:<8} | {'✅' if path else '❌'}")

        # 3. AStart (Python Adaptive)
        t0 = time.time()
        path = solver_py.solve(start, goal, k=K, adaptive=True)
        t_py_adapt = time.time() - t0
        print(f"{name:<15} | {'Py Batch A* (Adaptive)':<25} | {t_py_adapt:<10.5f} | {len(path) if path else 0:<8} | {'✅' if path else '❌'}")

        # 4. AStart (C++ Native Batch A* - Optimized)
        solver_cpp = AStart(adj, heuristic_func='manhattan', use_cpp=True)
        t0 = time.time()
        path = solver_cpp.solve(start, goal, k=K, adaptive=False)
        t_cpp_fixed = time.time() - t0
        print(f"{name:<15} | {'C++ Batch (Native)':<25} | {t_cpp_fixed:<10.5f} | {len(path) if path else 0:<8} | {'✅' if path else '❌'}")

        # 5. AStart (C++ Native Adaptive - Optimized)
        t0 = time.time()
        path = solver_cpp.solve(start, goal, k=K, adaptive=True)
        t_cpp_adapt = time.time() - t0
        print(f"{name:<15} | {'C++ Adaptive (Native)':<25} | {t_cpp_adapt:<10.5f} | {len(path) if path else 0:<8} | {'✅' if path else '❌'}")
        
        # 6. C++ Batch (Dijkstra - No Heuristic)
        solver_cpp_dij = AStart(adj, heuristic_func=None, use_cpp=True)
        t0 = time.time()
        path = solver_cpp_dij.solve(start, goal, k=K, adaptive=False)
        t_cpp_dij = time.time() - t0
        print(f"{name:<15} | {'C++ Batch (Dijkstra)':<25} | {t_cpp_dij:<10.5f} | {len(path) if path else 0:<8} | {'✅' if path else '❌'}")

        print("-" * 75)

if __name__ == "__main__":
    run_suite()
