use rust_astart::Solver;
use std::time::Instant;
use rand::Rng;

fn main() {
    let n = 100; // 100x100 grid = 10,000 nodes
    let num_nodes = n * n;
    println!("Generating {}x{} Graph ({} nodes) with shortcuts...", n, n, num_nodes);

    let mut graph = vec![Vec::new(); num_nodes];
    let mut rng = rand::thread_rng();

    // 1. Grid Edges
    for r in 0..n {
        for c in 0..n {
            let u = r * n + c;
            // Right
            if c + 1 < n {
                let v = r * n + (c + 1);
                let w = rng.gen_range(1..10);
                graph[u].push((v, w));
                graph[v].push((u, w));
            }
            // Down
            if r + 1 < n {
                let v = (r + 1) * n + c;
                let w = rng.gen_range(1..10);
                graph[u].push((v, w));
                graph[v].push((u, w));
            }
        }
    }

    // 2. Shortcuts (Teleporters)
    let num_shortcuts = num_nodes * 2;
    for _ in 0..num_shortcuts {
        let u = rng.gen_range(0..num_nodes);
        let v = rng.gen_range(0..num_nodes);
        if u != v {
            let w = rng.gen_range(1..50);
            graph[u].push((v, w));
            graph[v].push((u, w)); // Undirected
        }
    }

    let solver = Solver::new(graph);
    let start = 0;
    let goal = num_nodes - 1;

    // --- Standard A* ---
    println!("\nRunning Standard A* (Rust)...\n");
    let t0 = Instant::now();
    let (cost_std, stats_std) = solver.solve_std(start, goal);
    let t1 = t0.elapsed();
    println!("Time: {{:.6?}}s", t1);
    println!("Cost: {{:?}}", cost_std);
    println!("Stats: {{:?}}", stats_std);

    // --- Batch A* ---
    let k = 10;
    println!("\nRunning Batch A* (k={{}}, Rust)...\n", k);
    let t0 = Instant::now();
    let (cost_batch, stats_batch) = solver.solve_batch(start, goal, k);
    let t1 = t0.elapsed();
    println!("Time: {{:.6?}}s", t1);
    println!("Cost: {{:?}}", cost_batch);
    println!("Stats: {{:?}}", stats_batch);

    if cost_std == cost_batch {
        println!("\n✅ SUCCESS: Costs match.\n");
    } else {
        println!("\n❌ MISMATCH: Standard={{:?}}, Batch={{:?}}\n", cost_std, cost_batch);
    }
    
    let reduction = stats_std.heap_pushes as f64 / stats_batch.heap_pushes as f64;
    println!("Heap Pushes Reduced by: {{:.2}}x\n", reduction);
}
