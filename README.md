# AStart (Batch A\*)

A simple implementation of the **Batch A\* (Frontier Reduction)** algorithm. This repository contains a pure Python package for ease of use, along with C++ and Rust implementations for performance benchmarking.

## What is Batch A\*?

Batch A* is a variation of the A* search algorithm designed to reduce the overhead of Priority Queue (Heap) operations. Instead of pushing every neighbor to the heap immediately, it performs a local "relaxation" search (Bellman-Ford style) for `k` steps.

**It shines when:**

- **Heuristics are Expensive:** (e.g., Robotics, AI) Reduces heuristic calls by 10x+.
- **Massive Graphs:** Reduces random memory/disk access by processing nodes in batches.

---

## 🐍 Python Package

### Installation

```bash
pip install -e .
```

### Usage

```python
from astart import AStart

# 1. Define your graph (Dict of Dicts)
graph = {
    'A': {'B': 1, 'C': 3},
    'B': {'D': 2},
    'C': {'D': 1},
    'D': {}
}

# 2. Define Heuristic (Optional)
# Use h=0 for Dijkstra behavior (guaranteed optimal on all graphs)
def heuristic(u, goal):
    return 0

# 3. Solve
solver = AStart(graph, heuristic)
path = solver.solve('A', 'D', k=10)
print(path) # ['A', 'C', 'D']
```

### Examples

- `examples/comparison.py`: Compares Standard A* vs Batch A* on a random grid.
- `examples/expensive_heuristic.py`: Demonstrates the speedup when the heuristic function is slow.

---

## ⚡ Benchmarks (C++ & Rust)

This repository includes high-performance implementations to demonstrate the algorithm's raw efficiency.

### C++

Located in `benchmarks/cpp/`. Requires `clang++` or `g++`.

```bash
cd benchmarks/cpp
clang++ -O3 main.cpp -o benchmark
./benchmark
```

_Typical Result: ~12x reduction in Heap Pushes._

### Rust

Located in `benchmarks/rust/`. Requires `cargo`.

```bash
cd benchmarks/rust
cargo run --release
```

---

## License

MIT
