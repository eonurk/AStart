# AStart (Batch A*)

A high-performance implementation of the Batch A* (Frontier Reduction) algorithm. This package features a hybrid Python/C++ engine, providing significant performance gains over pure Python implementations while maintaining a simple Python API.

## Algorithm Overview

Batch A* is a variation of A* designed to minimize Priority Queue (Heap) overhead. Instead of pushing every neighbor to the heap immediately, it performs a local relaxation search for `k` steps before committing nodes to the global heap.

### Advantages
1.  **Efficiency:** Reduces Heap operations by 1.2x - 12x.
2.  **Robustness:** Finds optimal paths on complex graphs (e.g., with inconsistent heuristics) where standard A* with a closed set can return suboptimal results.
3.  **Expensive Heuristics:** Reduces calls to the heuristic function by 10x+, which is ideal when the function involves complex computations.

## Installation

```bash
pip install .
```
A C++ compiler (g++ or clang++) is required to build the optimized backend.

## Usage

### Basic Usage (C++ Backend)

By default, the solver uses the C++ backend for maximum speed.

```python
from astart import AStart

# Define your graph (Dict of Dicts)
graph = {
    'A': {'B': 1, 'C': 3},
    'B': {'D': 2},
    'C': {'D': 1},
    'D': {}
}

# Initialize Solver
solver = AStart(graph) 

# Solve
path = solver.solve('A', 'D', k=10)
print(path) # ['A', 'C', 'D']
```

### Custom Heuristics (Python Fallback)

If a custom heuristic function is provided, the solver automatically falls back to the pure Python implementation.

```python
def manhattan(u, goal):
    return abs(u[0] - goal[0]) + abs(u[1] - goal[1])

solver = AStart(grid_graph, heuristic_func=manhattan)
```

## Advanced Features

### Adaptive Batching (Gradient Descent)

For graphs with expensive traps or where you want to minimize node relaxations, use `adaptive=True`.

**Logic:**
The algorithm continues the local batch expansion only as long as the heuristic `h(n)` improves (Gradient Descent). If `h(n)` worsens (uphill), it stops the batch immediately and pushes to the heap.

```python
# Use Adaptive Batching
path = solver.solve(start, goal, k=20, adaptive=True)
```

*   **Best for:** Complex Mazes, Traps, Cheap Heuristics.
*   **Trade-off:** Increases Heap operations but drastically reduces blind node expansions.

## Benchmarks (Moving AI)

The following results are the **verified average performance across 20 representative maps** (Small to Huge) in the Dragon Age: Origins dataset from the Moving AI Lab.

| Algorithm | Language | Avg Search Time | Speedup | Path Overhead |
| :--- | :--- | :--- | :--- | :--- |
| Standard A* (Classic) | C++ | 1.273 ms | 1.0x | 0.00% |
| NetworKit (Industrial) | C++ | 13.789 ms | 0.09x | 0.00% |
| **AStart (Batch-1000)** | **C++** | **0.623 ms** | **2.04x** | **0.00%** |

### Key Takeaways
1. **Double the Performance**: `AStart` consistently delivers a **2x speedup** over standard C++ A* by reducing Priority Queue updates.
2. **Extreme Efficiency**: It is **22x faster** than industrial libraries like NetworKit for grid-based navigation.
3. **Perfect Precision**: On the DAO dataset, Batch A* achieved **0% path overhead**, maintaining total optimality while being significantly faster.

---

## Performance

Benchmarks comparing **Standard A*** (`k=1`) vs **Batch A*** (`k=20`) running natively in C++:

| Scenario | Algorithm | Time (s) | Speedup |
| :--- | :--- | :--- | :--- |
| **Open Grid** | Standard A* | 0.0050s | 1.0x |
| | **Batch A* (Fixed)** | **0.0029s** | **1.7x** |
| **Maze** | Standard A* | 0.0036s | 1.0x |
| | **Batch A* (Fixed)** | **0.0013s** | **2.8x** |

*Note: While Adaptive Batching prevents "flooding" in specific traps, **Fixed Batching** generally yields the highest raw throughput in C++.*

## Project Structure

*   `astart/`: Core package (Python wrapper and C++ source).
*   `examples/`: Sample scripts for performance comparison and edge cases.
*   `tests/`: Unit tests for verifying correctness.
*   `benchmarks/`: Standalone Rust and C++ implementations for research.

## License

MIT
