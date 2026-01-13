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

## Performance

| Backend | Time (10k Nodes) | Speedup |
| :--- | :--- | :--- |
| Pure Python | ~0.030s | 1x |
| C++ Engine | ~0.0015s | 20x |

## Project Structure

*   `astart/`: Core package (Python wrapper and C++ source).
*   `examples/`: Sample scripts for performance comparison and edge cases.
*   `tests/`: Unit tests for verifying correctness.
*   `benchmarks/`: Standalone Rust and C++ implementations for research.

## License

MIT
