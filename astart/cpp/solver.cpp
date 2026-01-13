#include <vector>
#include <queue>
#include <algorithm>
#include <unordered_map>
#include <limits>

// --- Data Structures ---
const unsigned int INF = std::numeric_limits<unsigned int>::max();

struct Edge {
    int to;
    int weight;
};

class GraphSolver {
public:
    std::vector<std::vector<Edge>> adj;
    
    GraphSolver(int num_nodes) {
        adj.resize(num_nodes);
    }

    void add_edge(int u, int v, int w) {
        if (u >= adj.size() || v >= adj.size()) {
            // Resize if necessary (though we expect num_nodes to be accurate)
            int new_size = std::max(u, v) + 1;
            if (new_size > adj.size()) adj.resize(new_size);
        }
        adj[u].push_back({v, w});
    }

    // Returns path as a vector of node IDs. 
    // Returns empty vector if no path.
    // Writes path to 'out_path' array pointer and returns length.
    int solve(int start, int goal, int k, int* out_path, int max_len) {
        if (start >= adj.size() || goal >= adj.size()) return 0;

        // Dijkstra/A* (h=0) Priority Queue
        // Pair: <cost, u>
        using PII = std::pair<unsigned int, int>;
        std::priority_queue<PII, std::vector<PII>, std::greater<PII>> open_set;
        
        std::vector<unsigned int> g_score(adj.size(), INF);
        std::vector<int> came_from(adj.size(), -1);
        std::vector<bool> visited_pivots(adj.size(), false);
        
        g_score[start] = 0;
        open_set.push({0, start});
        
        // Buffers for batching
        std::vector<int> frontier;
        std::vector<int> next_frontier;
        std::vector<int> next_pivots;
        frontier.reserve(1000);

        while (!open_set.empty()) {
            auto [current_f, current_u] = open_set.top();
            open_set.pop();
            
            if (visited_pivots[current_u]) continue;
            visited_pivots[current_u] = true;
            
            if (current_u == goal) {
                return reconstruct_path(came_from, current_u, out_path, max_len);
            }
            
            // Optimization: If found a better path to current_u already? 
            // Checked by g_score vs current_f implicitly, but visited_pivots handles it.

            // --- Batch Expansion ---
            frontier.clear();
            frontier.push_back(current_u);
            next_pivots.clear();
            
            for (int step = 0; step < k; ++step) {
                next_frontier.clear();
                
                for (int u : frontier) {
                    for (const auto& edge : adj[u]) {
                        int v = edge.to;
                        int w = edge.weight;
                        
                        unsigned int tentative = g_score[u] + w;
                        if (tentative < g_score[v]) {
                            g_score[v] = tentative;
                            came_from[v] = u;
                            next_frontier.push_back(v);
                            
                            // Capture internal goal
                            if (v == goal) next_pivots.push_back(v);
                        }
                    }
                }
                
                if (next_frontier.empty()) {
                    // Dead end / Exhausted -> capture boundary
                    for(int n : frontier) next_pivots.push_back(n);
                    break;
                }
                
                frontier = next_frontier;
                
                if (step == k - 1) {
                    for(int n : frontier) next_pivots.push_back(n);
                }
            }
            
            // Push Pivots
            for (int pivot : next_pivots) {
                // Dijkstra: f = g
                open_set.push({g_score[pivot], pivot});
            }
        }
        
        return 0; // No path
    }

private:
    int reconstruct_path(const std::vector<int>& came_from, int current, int* out_path, int max_len) {
        std::vector<int> path;
        while (current != -1) {
            path.push_back(current);
            current = came_from[current];
        }
        std::reverse(path.begin(), path.end());
        
        int len = std::min((int)path.size(), max_len);
        for (int i = 0; i < len; ++i) {
            out_path[i] = path[i];
        }
        return len;
    }
};

// --- C Interface for ctypes ---
extern "C" {
    GraphSolver* Solver_new(int num_nodes) {
        return new GraphSolver(num_nodes);
    }

    void Solver_delete(GraphSolver* solver) {
        delete solver;
    }

    void Solver_add_edge(GraphSolver* solver, int u, int v, int w) {
        solver->add_edge(u, v, w);
    }

    int Solver_solve(GraphSolver* solver, int start, int goal, int k, int* out_path, int max_len) {
        return solver->solve(start, goal, k, out_path, max_len);
    }
}
