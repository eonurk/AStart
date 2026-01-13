import heapq
from collections import defaultdict

class AStart:
    def __init__(self, graph_adj, heuristic_func=None):
        """
        Args:
            graph_adj: Dict of Dicts {u: {v: weight, ...}, ...}
            heuristic_func: Function h(u, goal) -> float. (Defaults to Dijkstra/0)
        """
        self.graph = graph_adj
        self.h = heuristic_func if heuristic_func else (lambda u, g: 0)
        self.stats = {'expansions': 0, 'heap_pushes': 0, 'nodes_relaxed': 0}

    def solve(self, start, goal, k=5):
        """
        Runs the Batch A* (Frontier Reduction) algorithm.
        
        Args:
            start: Start node ID
            goal: Goal node ID
            k: Batch size (The 'Lookahead' steps). 
               Higher k = fewer heap operations but more local re-scanning.
               k=1 is identical to Standard A*.
        """
        # 1. Initialization
        # Global Open Set: Stores (f_score, node_id)
        # We assume strict ordering isn't needed within the batch, only between batches.
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        
        came_from = {}
        
        visited_pivots = set()

        while open_set:
            # --- Global Step: Pick the best Pivot ---
            current_f, current_u = heapq.heappop(open_set)
            
            if current_u in visited_pivots:
                continue
            visited_pivots.add(current_u)
            self.stats['expansions'] += 1

            if current_u == goal:
                return self._reconstruct_path(came_from, current_u)

            # --- Local Step: Frontier Reduction (The Paper's Logic) ---
            # Instead of adding neighbors to Heap, we relax for k steps locally.
            
            # 'frontier' acts as our local working set (the "Batch")
            frontier = {current_u}
            
            # We track which nodes are the "output" of this batch to be pushed to Heap
            next_pivots = set()

            for step in range(k):
                next_frontier = set()
                
                for u in frontier:
                    # Relax edges (Bellman-Ford style expansion)
                    if u not in self.graph: continue
                    
                    for v, weight in self.graph[u].items():
                        self.stats['nodes_relaxed'] += 1
                        tentative_g = g_score[u] + weight
                        
                        if tentative_g < g_score[v]:
                            came_from[v] = u
                            g_score[v] = tentative_g
                            next_frontier.add(v)
                            # CRITICAL: If we see the goal, ensure it becomes a pivot 
                            # so it can be popped from the global heap to trigger success.
                            if v == goal:
                                next_pivots.add(v)
                
                if not next_frontier:
                    # If local search dries up, push the boundary nodes to heap.
                    next_pivots.update(frontier)
                    break
                    
                frontier = next_frontier
                
                # In the final step, everything in the frontier becomes a Pivot
                if step == k - 1:
                    next_pivots.update(frontier)
                else:
                    # Optimization: If the frontier is getting huge, we might 
                    # want to treat them as pivots early (similar to the paper's |W| > k|S| check).
                    # For this implementation, we stick to strict k-step depth.
                    pass

            # --- Batch Push ---
            # Only push the survivors (Pivots) of the k-step process to the Global Heap
            for pivot in next_pivots:
                # Calculate f-score lazily only when pushing to heap
                f_cost = g_score[pivot] + self.h(pivot, goal)
                heapq.heappush(open_set, (f_cost, pivot))
                self.stats['heap_pushes'] += 1

        return None # No path found

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]