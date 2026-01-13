# AStart (Batch A*)

A high-performance, robust implementation of the **Batch A* (Frontier Reduction)** algorithm. This package features a **hybrid Python/C++ engine**, delivering **20x faster performance** while maintaining the ease of use of Python.

## 🌟 Why Batch A*?

Batch A* is a variation of A* designed to minimize **Priority Queue (Heap) overhead**. Instead of pushing every neighbor to the heap immediately, it performs a local "relaxation" search (Bellman-Ford style) for `k` steps.

### Key Advantages:
1.  **🚀 Speed:** Reduces Heap `push`/`pop` operations by **1.2x - 12x**.
2.  **🛡️ Robustness:** Proven to find optimal paths on complex graphs (e.g., with "Wormholes" or inconsistent heuristics) where Standard A* can return suboptimal results.
3.  **🤖 Expensive Heuristics:** If your heuristic (`h(n)`) is slow (e.g., Neural Network or Physics check), Batch A* reduces calls by **10x+**.

---

## 📦 Installation

```bash
pip install .
```
*Note: This automatically compiles the C++ backend. You need a C++ compiler (`g++` or `clang++`) installed.*

---

## 💻 Usage

### Basic Usage (Fast C++ Backend)

By default, `AStart` uses the optimized C++ backend (Dijkstra mode, `h=0`) for maximum speed.

```python
from astart import AStart

# 1. Define your graph (Dict of Dicts)
graph = {
    'A': {'B': 1, 'C': 3},
    'B': {'D': 2},
    'C': {'D': 1},
    'D': {}
}

# 2. Initialize Solver
solver = AStart(graph) 

# 3. Solve (k=10 lookahead)
path = solver.solve('A', 'D', k=10)
print(path) # ['A', 'C', 'D']
```

### Custom Heuristics (Python Fallback)

If you need a custom heuristic function, the solver automatically falls back to the pure Python implementation.

```python
def manhattan(u, goal):
    return abs(u[0] - goal[0]) + abs(u[1] - goal[1])

# This will run in Python mode
solver = AStart(grid_graph, heuristic_func=manhattan)
```

---

## ⚡ Performance

| Backend | Time (10k Nodes) | Speedup |
| :--- | :--- | :--- |
| **Pure Python** | ~0.030s | 1x |
| **C++ Engine** | **~0.0015s** | **20x** |

*(Benchmark run on M1 MacBook Pro, 100x100 Grid)*

---

## 📂 Examples

Check the `examples/` directory for verified scenarios:

*   **`comparison.py`**: Performance comparison between Standard A* and Batch A*.
*   **`complex_failure_case.py`**: Demonstrates how Batch A* solves "Wormhole" graphs where Standard A* fails.
*   **`expensive_heuristic.py`**: Shows massive speedups when `h(n)` is computationally expensive.

---

## 🔬 Standalone Benchmarks

For research or porting, standalone implementations are available:

*   **Rust:** `benchmarks/rust/` (Run with `cargo run --release`)
*   **C++:** `benchmarks/cpp/` (Compile with `clang++ -O3`)

---

## License

MIT License. Free for open-source and commercial use.