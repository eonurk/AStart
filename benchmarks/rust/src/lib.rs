use std::cmp::Reverse;
use std::collections::BinaryHeap;

#[derive(Debug, Default, Clone)]
pub struct Stats {
    pub expansions: usize,
    pub heap_pushes: usize,
    pub nodes_relaxed: usize,
}

pub struct Solver {
    graph: Vec<Vec<(usize, u32)>>,
}

impl Solver {
    pub fn new(graph: Vec<Vec<(usize, u32)>>) -> Self {
        Self { graph }
    }

    // Standard A* (Simulated as k=1 or just pure implementation)
    // We implement it purely for fair comparison.
    pub fn solve_std(&self, start: usize, goal: usize) -> (Option<u32>, Stats) {
        let mut stats = Stats::default();
        let mut open_set = BinaryHeap::new();
        let mut g_score = vec![u32::MAX; self.graph.len()];
        let mut visited_pivots = vec![false; self.graph.len()]; // Closed Set

        g_score[start] = 0;
        open_set.push((Reverse(0), start));
        stats.heap_pushes += 1;

        while let Some((Reverse(current_f), current_u)) = open_set.pop() {
            if visited_pivots[current_u] {
                continue;
            }
            visited_pivots[current_u] = true;
            stats.expansions += 1;

            if current_u == goal {
                return (Some(g_score[current_u]), stats);
            }

            // Using h=0 (Dijkstra) for consistency
            if current_f > g_score[current_u] {
                continue;
            }

            for &(v, w) in &self.graph[current_u] {
                stats.nodes_relaxed += 1;
                let tentative_g = g_score[current_u] + w;
                if tentative_g < g_score[v] {
                    g_score[v] = tentative_g;
                    let f = tentative_g; // + h(0)
                    open_set.push((Reverse(f), v));
                    stats.heap_pushes += 1;
                }
            }
        }
        (None, stats)
    }

    pub fn solve_batch(&self, start: usize, goal: usize, k: usize) -> (Option<u32>, Stats) {
        let mut stats = Stats::default();
        let mut open_set = BinaryHeap::new();
        let mut g_score = vec![u32::MAX; self.graph.len()];
        let mut visited_pivots = vec![false; self.graph.len()];

        g_score[start] = 0;
        open_set.push((Reverse(0), start));
        stats.heap_pushes += 1;

        // Re-usable buffers to avoid allocation
        let mut frontier = Vec::new();
        let mut next_frontier = Vec::new();
        let mut next_pivots = Vec::new();

        while let Some((Reverse(_current_f), current_u)) = open_set.pop() {
            if visited_pivots[current_u] {
                continue;
            }
            visited_pivots[current_u] = true;
            stats.expansions += 1;

            if current_u == goal {
                return (Some(g_score[current_u]), stats);
            }

            // --- Local Step (Frontier Reduction) ---
            frontier.clear();
            frontier.push(current_u);
            next_pivots.clear();

            for step in 0..k {
                next_frontier.clear();

                for &u in &frontier {
                    for &(v, w) in &self.graph[u] {
                        stats.nodes_relaxed += 1;
                        let tentative_g = g_score[u].saturating_add(w);
                        
                        if tentative_g < g_score[v] {
                            g_score[v] = tentative_g;
                            next_frontier.push(v);
                            
                            // FIX: Internal Goal Capture
                            if v == goal {
                                next_pivots.push(v);
                            }
                        }
                    }
                }

                if next_frontier.is_empty() {
                    // FIX: Dead end capture
                    next_pivots.extend_from_slice(&frontier);
                    break;
                }

                // Optimization: Deduplicate next_frontier?
                // For a grid, duplicates are common. Sorting/deduping is costly but prevents exponential growth.
                // For now, naive.
                
                std::mem::swap(&mut frontier, &mut next_frontier);

                if step == k - 1 {
                    next_pivots.extend_from_slice(&frontier);
                }
            }

            // --- Batch Push ---
            for &pivot in &next_pivots {
                // We don't check visited here because re-evaluating with better g is allowed/handled by heap.
                // h=0 (Dijkstra)
                let f = g_score[pivot]; 
                open_set.push((Reverse(f), pivot));
                stats.heap_pushes += 1;
            }
        }
        (None, stats)
    }
}
