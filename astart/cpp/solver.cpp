#include <vector>
#include <queue>
#include <algorithm>
#include <cmath>
#include <unordered_map>
#include <limits>

const float INF = std::numeric_limits<float>::infinity();

struct Edge {
    int to;
    float weight;
};

class GraphSolver {
public:
    std::vector<std::vector<Edge>> adj;
    int num_nodes;
    int width;
    
    GraphSolver(int n) : num_nodes(n), width(0) {
        adj.resize(n);
    }

    void set_width(int w) { width = w; }

    void add_edge(int u, int v, float w) {
        if (u < adj.size() && v < adj.size()) {
            adj[u].push_back({v, w});
        }
    }

    inline float calculate_h(int u, int goal, int mode, float* h_array) {
        if (mode == 0) return 0;
        if (mode == 2 && h_array) return h_array[u];
        
        // Native Grid Logic
        if (width <= 0) return 0;
        int x1 = u % width;
        int y1 = u / width;
        int x2 = goal % width;
        int y2 = goal / width;
        float dx = std::abs(x1 - x2);
        float dy = std::abs(y1 - y2);

        if (mode == 1) return dx + dy; // Manhattan
        if (mode == 3) return (dx + dy) + (1.41421356f - 2.0f) * std::min(dx, dy); // Octile
        return 0;
    }

    int solve_classic(int start, int goal, int heuristic_mode, float* h_values, int* out_path, int max_len) {
        if (start >= (int)adj.size() || goal >= (int)adj.size()) return 0;

        using PII = std::pair<float, int>;
        std::priority_queue<PII, std::vector<PII>, std::greater<PII>> open_set;
        
        std::vector<float> g_score(adj.size(), INF);
        std::vector<int> came_from(adj.size(), -1);
        std::vector<bool> visited(adj.size(), false);
        
        g_score[start] = 0;
        open_set.push({calculate_h(start, goal, heuristic_mode, h_values), start});

        while (!open_set.empty()) {
            int u = open_set.top().second;
            open_set.pop();
            
            if (visited[u]) continue;
            visited[u] = true;
            
            if (u == goal) return reconstruct_path(came_from, u, out_path, max_len);

            for (const auto& edge : adj[u]) {
                int v = edge.to;
                float tentative = g_score[u] + edge.weight;
                if (tentative < g_score[v]) {
                    g_score[v] = tentative;
                    came_from[v] = u;
                    open_set.push({tentative + calculate_h(v, goal, heuristic_mode, h_values), v});
                }
            }
        }
        return 0;
    }

    int solve(int start, int goal, int k, int adaptive, int heuristic_mode, float* h_values, int* out_path, int max_len) {
        if (start >= (int)adj.size() || goal >= (int)adj.size()) return 0;

        using PII = std::pair<float, int>;
        std::priority_queue<PII, std::vector<PII>, std::greater<PII>> open_set;
        
        std::vector<float> g_score(adj.size(), INF);
        std::vector<int> came_from(adj.size(), -1);
        std::vector<bool> visited_pivots(adj.size(), false);
        
        g_score[start] = 0;
        float h_start = calculate_h(start, goal, heuristic_mode, h_values);
        open_set.push({h_start, start});
        
        std::vector<int> frontier;
        std::vector<int> next_frontier;
        std::vector<int> next_pivots;
        frontier.reserve(65536);
        next_frontier.reserve(65536);
        next_pivots.reserve(65536);

        while (!open_set.empty()) {
            auto [current_f, current_u] = open_set.top();
            open_set.pop();
            
            if (visited_pivots[current_u]) continue;
            visited_pivots[current_u] = true;
            
            if (current_u == goal) return reconstruct_path(came_from, current_u, out_path, max_len);

            frontier.clear();
            frontier.push_back(current_u);
            next_pivots.clear();
            
            for (int step = 0; step < k; ++step) {
                next_frontier.clear();
                for (int u : frontier) {
                    float h_u = (adaptive) ? calculate_h(u, goal, heuristic_mode, h_values) : 0;
                    for (const auto& edge : adj[u]) {
                        int v = edge.to;
                        float w = edge.weight;
                        float tentative = g_score[u] + w;
                        if (tentative < g_score[v]) {
                            g_score[v] = tentative;
                            came_from[v] = u;
                            if (adaptive && calculate_h(v, goal, heuristic_mode, h_values) > h_u) {
                                next_pivots.push_back(v);
                            } else {
                                next_frontier.push_back(v);
                                if (v == goal) return reconstruct_path(came_from, goal, out_path, max_len);
                            }
                        }
                    }
                }
                if (next_frontier.empty()) {
                    for(int n : frontier) next_pivots.push_back(n);
                    break;
                }
                std::swap(frontier, next_frontier);
                if (step == k - 1) {
                    for(int n : frontier) next_pivots.push_back(n);
                }
            }
            for (int pivot : next_pivots) {
                open_set.push({g_score[pivot] + calculate_h(pivot, goal, heuristic_mode, h_values), pivot});
            }
        }
        return 0;
    }

private:
    int reconstruct_path(const std::vector<int>& came_from, int current, int* out_path, int max_len) {
        std::vector<int> path;
        while (current != -1) {
            path.push_back(current);
            current = (current < (int)came_from.size()) ? came_from[current] : -1;
        }
        std::reverse(path.begin(), path.end());
        int len = std::min((int)path.size(), max_len);
        for (int i = 0; i < len; ++i) out_path[i] = path[i];
        return len;
    }
};

extern "C" {
    GraphSolver* Solver_new(int num_nodes) { return new GraphSolver(num_nodes); }
    void Solver_delete(GraphSolver* solver) { delete solver; }
    void Solver_set_width(GraphSolver* solver, int w) { solver->set_width(w); }
    void Solver_add_edge(GraphSolver* solver, int u, int v, float w) { solver->add_edge(u, v, w); }
    int Solver_solve_classic(GraphSolver* solver, int start, int goal, int heuristic_mode, float* h_values, int* out_path, int max_len) {
        return solver->solve_classic(start, goal, heuristic_mode, h_values, out_path, max_len);
    }
    int Solver_solve(GraphSolver* solver, int start, int goal, int k, int adaptive, int heuristic_mode, float* h_values, int* out_path, int max_len) {
        return solver->solve(start, goal, k, adaptive, heuristic_mode, h_values, out_path, max_len);
    }
}
