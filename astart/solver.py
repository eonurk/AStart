import heapq
import ctypes
import os
import glob
from collections import defaultdict
import math

_cpp_lib = None
# Find the compiled extension module in the installed package or local folder
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Check for installed location first
    import astart._cpp_backend as backend
    _cpp_lib = ctypes.CDLL(backend.__file__)
except Exception as e:
    # Fallback to glob for development
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_files = glob.glob(os.path.join(current_dir, "*_cpp_backend*"))
        if not lib_files:
            lib_files = glob.glob(os.path.join(current_dir, "..", "*_cpp_backend*"))
        if lib_files:
            _cpp_lib = ctypes.CDLL(lib_files[0])
    except: pass

if _cpp_lib:
    _cpp_lib.Solver_new.argtypes = [ctypes.c_int]
    _cpp_lib.Solver_new.restype = ctypes.c_void_p
    _cpp_lib.Solver_delete.argtypes = [ctypes.c_void_p]
    _cpp_lib.Solver_set_width.argtypes = [ctypes.c_void_p, ctypes.c_int]
    _cpp_lib.Solver_add_edge.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    _cpp_lib.Solver_solve_classic.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, 
        ctypes.c_int, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_int), ctypes.c_int
    ]
    _cpp_lib.Solver_solve_classic.restype = ctypes.c_int
    _cpp_lib.Solver_solve.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
        ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_int), ctypes.c_int
    ]
    _cpp_lib.Solver_solve.restype = ctypes.c_int

class AStart:
    def __init__(self, graph_adj, heuristic_func=None, use_cpp=True):
        self.graph = graph_adj
        self.h = heuristic_func
        self.use_cpp = use_cpp and (_cpp_lib is not None)
        if use_cpp and not _cpp_lib:
            raise RuntimeError("C++ Backend requested but not found!")
            
        self._cpp_solver = None
        self._id_to_node = []
        self._node_to_id = {}
        if self.use_cpp:
            self._init_cpp_graph()

    def _init_cpp_graph(self):
        nodes = set(self.graph.keys())
        first_key = next(iter(self.graph)) if self.graph else None
        is_grid = isinstance(first_key, tuple)
        
        if is_grid:
             self._id_to_node = sorted(list(nodes), key=lambda p: (p[1], p[0]))
        else:
             for u, nbrs in self.graph.items():
                 for v in nbrs: nodes.add(v)
             self._id_to_node = list(nodes)
             
        self._node_to_id = {n: i for i, n in enumerate(self._id_to_node)}
        self._cpp_solver = _cpp_lib.Solver_new(len(self._id_to_node))
        
        if is_grid:
            min_x = min(n[0] for n in self._id_to_node)
            max_x = max(n[0] for n in self._id_to_node)
            _cpp_lib.Solver_set_width(self._cpp_solver, int(max_x - min_x + 1))
            
        for u, nbrs in self.graph.items():
            u_id = self._node_to_id[u]
            for v, w in nbrs.items():
                if v in self._node_to_id:
                    _cpp_lib.Solver_add_edge(self._cpp_solver, u_id, self._node_to_id[v], float(w))

    def __del__(self):
        if self._cpp_solver: _cpp_lib.Solver_delete(self._cpp_solver)

    def solve(self, start, goal, k=5, adaptive=False):
        return self._solve_cpp(start, goal, k, adaptive)

    def solve_classic(self, start, goal):
        if start not in self._node_to_id or goal not in self._node_to_id: return None
        h_mode = 0
        if self.h == 'manhattan': h_mode = 1
        elif self.h == 'octile': h_mode = 3
        max_len = 1000000 
        path_array = (ctypes.c_int * max_len)()
        p_len = _cpp_lib.Solver_solve_classic(self._cpp_solver, self._node_to_id[start], self._node_to_id[goal], h_mode, None, path_array, max_len)
        if p_len == 0: return None
        return [self._id_to_node[path_array[i]] for i in range(p_len)]

    def _solve_cpp(self, start, goal, k, adaptive):
        if start not in self._node_to_id or goal not in self._node_to_id: return None
        h_mode = 0
        h_array = None
        if self.h == 'manhattan': h_mode = 1
        elif self.h == 'octile': h_mode = 3
        elif callable(self.h):
            h_mode = 2
            num_nodes = len(self._id_to_node)
            h_array = (ctypes.c_float * num_nodes)()
            for i, node in enumerate(self._id_to_node):
                h_array[i] = float(self.h(node, goal))
        max_len = 1000000 
        path_array = (ctypes.c_int * max_len)()
        p_len = _cpp_lib.Solver_solve(self._cpp_solver, self._node_to_id[start], self._node_to_id[goal], k, int(adaptive), h_mode, h_array, path_array, max_len)
        if p_len == 0: return None
        return [self._id_to_node[path_array[i]] for i in range(p_len)]