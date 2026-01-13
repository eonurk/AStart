#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <random>
#include <unordered_map>
#include <chrono>
#include <limits>
#include <iomanip>
#include <set>

using namespace std;

const unsigned int INF = numeric_limits<unsigned int>::max();

struct Stats {
    long long expansions = 0;
    long long heap_pushes = 0;
    long long nodes_relaxed = 0;
};

// Adjacency list: node -> vector of (neighbor, weight)
using Graph = vector<vector<pair<int, int>>>;

struct Node {
    unsigned int f;
    int u;
    
    bool operator>(const Node& other) const {
        return f > other.f;
    }
};

// Standard A* (Dijkstra with h=0 for consistency)
pair<unsigned int, Stats> solve_std(const Graph& graph, int start, int goal) {
    Stats stats;
    priority_queue<Node, vector<Node>, greater<Node>> open_set;
    vector<unsigned int> g_score(graph.size(), INF);
    vector<bool> visited(graph.size(), false);
    
    g_score[start] = 0;
    open_set.push({0, start});
    stats.heap_pushes++;
    
    while (!open_set.empty()) {
        Node current = open_set.top();
        open_set.pop();
        int u = current.u;
        
        if (visited[u]) continue;
        visited[u] = true;
        stats.expansions++;
        
        if (u == goal) return {g_score[u], stats};
        
        if (current.f > g_score[u]) continue;
        
        for (auto& edge : graph[u]) {
            int v = edge.first;
            int w = edge.second;
            stats.nodes_relaxed++;
            
            unsigned int tentative_g = g_score[u] + w;
            if (tentative_g < g_score[v]) {
                g_score[v] = tentative_g;
                open_set.push({tentative_g, v});
                stats.heap_pushes++;
            }
        }
    }
    return {INF, stats};
}

// Batch A* / Frontier Reduction
pair<unsigned int, Stats> solve_batch(const Graph& graph, int start, int goal, int k) {
    Stats stats;
    priority_queue<Node, vector<Node>, greater<Node>> open_set;
    vector<unsigned int> g_score(graph.size(), INF);
    vector<bool> visited(graph.size(), false);
    
    g_score[start] = 0;
    open_set.push({0, start});
    stats.heap_pushes++;
    
    // Buffers
    vector<int> frontier;
    vector<int> next_frontier;
    vector<int> next_pivots;
    frontier.reserve(1000);
    next_frontier.reserve(1000);
    next_pivots.reserve(1000);

    while (!open_set.empty()) {
        Node current = open_set.top();
        open_set.pop();
        int current_u = current.u;
        
        if (visited[current_u]) continue;
        visited[current_u] = true;
        stats.expansions++;
        
        if (current_u == goal) return {g_score[current_u], stats};
        
        // --- Local Step ---
        frontier.clear();
        frontier.push_back(current_u);
        next_pivots.clear();
        
        for (int step = 0; step < k; ++step) {
            next_frontier.clear();
            
            for (int u : frontier) {
                for (auto& edge : graph[u]) {
                    int v = edge.first;
                    int w = edge.second;
                    stats.nodes_relaxed++;
                    
                    unsigned int tentative_g = g_score[u] + w;
                    if (tentative_g < g_score[v]) {
                        g_score[v] = tentative_g;
                        next_frontier.push_back(v);
                        
                        if (v == goal) {
                            next_pivots.push_back(v);
                        }
                    }
                }
            }
            
            if (next_frontier.empty()) {
                // Dead end: capture surviving frontier
                next_pivots.insert(next_pivots.end(), frontier.begin(), frontier.end());
                break;
            }
            
            frontier = next_frontier; // move semantics or swap? swap is better
            // actually std::swap does not work well with iteration logic above if using references
            // but here we just re-assign. 
            // Better: swap logic
            // But 'next_frontier' needs to be cleared next loop. 
            // Simple assignment is fine for ints.
            
            if (step == k - 1) {
                next_pivots.insert(next_pivots.end(), frontier.begin(), frontier.end());
            }
        }
        
        // --- Batch Push ---
        for (int pivot : next_pivots) {
            open_set.push({g_score[pivot], pivot});
            stats.heap_pushes++;
        }
    }
    return {INF, stats};
}

int main() {
    int N = 100; // 100x100 grid
    int num_nodes = N * N;
    cout << "Generating " << N << "x" << N << " Graph (" << num_nodes << " nodes)..." << endl;
    
    Graph graph(num_nodes);
    mt19937 rng(12345); // Fixed seed for reproducibility
    uniform_int_distribution<int> weight_dist(1, 10);
    uniform_int_distribution<int> shortcut_w_dist(1, 50);
    uniform_int_distribution<int> node_dist(0, num_nodes - 1);
    
    // Grid edges
    for (int r = 0; r < N; ++r) {
        for (int c = 0; c < N; ++c) {
            int u = r * N + c;
            if (c + 1 < N) {
                int v = r * N + (c + 1);
                int w = weight_dist(rng);
                graph[u].push_back({v, w});
                graph[v].push_back({u, w});
            }
            if (r + 1 < N) {
                int v = (r + 1) * N + c;
                int w = weight_dist(rng);
                graph[u].push_back({v, w});
                graph[v].push_back({u, w});
            }
        }
    }
    
    // Shortcuts
    int num_shortcuts = num_nodes * 2;
    for (int i = 0; i < num_shortcuts; ++i) {
        int u = node_dist(rng);
        int v = node_dist(rng);
        if (u != v) {
            int w = shortcut_w_dist(rng);
            graph[u].push_back({v, w});
            graph[v].push_back({u, w});
        }
    }
    
    int start = 0;
    int goal = num_nodes - 1;
    
    // --- Run Standard ---
    cout << "\nRunning Standard A* (C++)..." << endl;
    auto t0 = chrono::high_resolution_clock::now();
    auto res_std = solve_std(graph, start, goal);
    auto t1 = chrono::high_resolution_clock::now();
    double time_std = chrono::duration<double>(t1 - t0).count();
    
    cout << "Time: " << fixed << setprecision(6) << time_std << "s" << endl;
    cout << "Cost: " << res_std.first << endl;
    cout << "Heap Pushes: " << res_std.second.heap_pushes << endl;
    
    // --- Run Batch ---
    int k = 10;
    cout << "\nRunning Batch A* (k=" << k << ", C++)..." << endl;
    t0 = chrono::high_resolution_clock::now();
    auto res_batch = solve_batch(graph, start, goal, k);
    t1 = chrono::high_resolution_clock::now();
    double time_batch = chrono::duration<double>(t1 - t0).count();
    
    cout << "Time: " << fixed << setprecision(6) << time_batch << "s" << endl;
    cout << "Cost: " << res_batch.first << endl;
    cout << "Heap Pushes: " << res_batch.second.heap_pushes << endl;
    
    if (res_std.first == res_batch.first) {
        cout << "\n✅ SUCCESS: Costs match." << endl;
    } else {
        cout << "\n❌ MISMATCH!" << endl;
    }
    
    cout << "Heap Pushes Reduced by: " << (double)res_std.second.heap_pushes / res_batch.second.heap_pushes << "x" << endl;
    
    return 0;
}
