import heapq
import ctypes
import os
import glob
from collections import defaultdict

# --- C++ Backend Loader ---
_cpp_lib = None
try:
    # Find the compiled extension module
    # It usually lives in the same directory as this file or one level up
    # Pattern: _cpp_backend*.so or _cpp_backend*.pyd
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_files = glob.glob(os.path.join(current_dir, "*_cpp_backend*"))
    
    if not lib_files:
        # Check parent dir (if installed in site-packages/astart/)
        lib_files = glob.glob(os.path.join(current_dir, "..", "*_cpp_backend*"))
        
    if lib_files:
        _cpp_lib = ctypes.CDLL(lib_files[0])
        
        # Define Argument Types
        _cpp_lib.Solver_new.argtypes = [ctypes.c_int]
        _cpp_lib.Solver_new.restype = ctypes.c_void_p
        
        _cpp_lib.Solver_delete.argtypes = [ctypes.c_void_p]
        
        _cpp_lib.Solver_add_edge.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        
        # solve(solver, start, goal, k, out_path_array, max_len)
        _cpp_lib.Solver_solve.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
            ctypes.POINTER(ctypes.c_int), ctypes.c_int
        ]
        _cpp_lib.Solver_solve.restype = ctypes.c_int
except Exception:
    pass


class AStart:
    def __init__(self, graph_adj, heuristic_func=None, use_cpp=True):
        """
        Args:
            graph_adj: Dict of Dicts {u: {v: weight, ...}, ...}
            heuristic_func: Function h(u, goal) -> float. (Defaults to Dijkstra/0)
            use_cpp: Whether to attempt using the C++ backend (if available and compatible).
        """
        self.graph = graph_adj
        self.h = heuristic_func
        self.stats = {'expansions': 0, 'heap_pushes': 0, 'nodes_relaxed': 0}
        
        self.use_cpp = use_cpp and (_cpp_lib is not None)
        
        # If user provides a custom heuristic, we MUST use Python
        # (unless we implemented callback logic, which we didn't for perf)
        if heuristic_func is not None:
            # We only support h=None (Dijkstra) in C++ for now
            self.use_cpp = False

        self._cpp_solver = None
        self._node_to_id = {}
        self._id_to_node = []
        
        if self.use_cpp:
            try:
                self._init_cpp_graph()
            except Exception as e:
                print(f"Warning: C++ Graph Init failed ({e}). Falling back to Python.")
                self.use_cpp = False

    def _init_cpp_graph(self):
        # 1. Map all nodes to IDs
        nodes = set(self.graph.keys())
        for u, neighbors in self.graph.items():
            for v in neighbors:
                nodes.add(v)
        
        self._id_to_node = list(nodes)
        self._node_to_id = {n: i for i, n in enumerate(self._id_to_node)}
        
        num_nodes = len(nodes)
        self._cpp_solver = _cpp_lib.Solver_new(num_nodes)
        
        # 2. Add Edges
        for u, neighbors in self.graph.items():
            u_id = self._node_to_id[u]
            for v, w in neighbors.items():
                v_id = self._node_to_id[v]
                _cpp_lib.Solver_add_edge(self._cpp_solver, u_id, v_id, int(w))

    def __del__(self):
        if self._cpp_solver:
            _cpp_lib.Solver_delete(self._cpp_solver)

    def solve(self, start, goal, k=5):
        if self.use_cpp:
            return self._solve_cpp(start, goal, k)
        else:
            return self._solve_python(start, goal, k)

    def _solve_cpp(self, start, goal, k):
        if start not in self._node_to_id or goal not in self._node_to_id:
            return None # Unknown nodes
            
        start_id = self._node_to_id[start]
        goal_id = self._node_to_id[goal]
        
        # Buffer for path result (max 1M nodes?)
        max_len = 1000000 
        path_array = (ctypes.c_int * max_len)()
        
        path_len = _cpp_lib.Solver_solve(self._cpp_solver, start_id, goal_id, k, path_array, max_len)
        
        if path_len == 0:
            return None
        
        # Convert IDs back to Python Objects
        path = []
        for i in range(path_len):
            node_id = path_array[i]
            path.append(self._id_to_node[node_id])
            
        return path

    def _solve_python(self, start, goal, k):
        # ... (Original Python Logic) ...
        # Copied from previous implementation
        h_func = self.h if self.h else (lambda u, g: 0)
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        
        came_from = {}
        visited_pivots = set()

        while open_set:
            current_f, current_u = heapq.heappop(open_set)
            
            if current_u in visited_pivots:
                continue
            visited_pivots.add(current_u)
            self.stats['expansions'] += 1

            if current_u == goal:
                return self._reconstruct_path(came_from, current_u)

            frontier = {current_u}
            next_pivots = set()

            for step in range(k):
                next_frontier = set()
                
                for u in frontier:
                    if u not in self.graph: continue
                    
                    for v, weight in self.graph[u].items():
                        self.stats['nodes_relaxed'] += 1
                        tentative_g = g_score[u] + weight
                        
                        if tentative_g < g_score[v]:
                            came_from[v] = u
                            g_score[v] = tentative_g
                            next_frontier.add(v)
                            if v == goal:
                                next_pivots.add(v)
                
                if not next_frontier:
                    next_pivots.update(frontier)
                    break
                    
                frontier = next_frontier
                
                if step == k - 1:
                    next_pivots.update(frontier)

            for pivot in next_pivots:
                f_cost = g_score[pivot] + h_func(pivot, goal)
                heapq.heappush(open_set, (f_cost, pivot))
                self.stats['heap_pushes'] += 1

        return None

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
