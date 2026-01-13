from astart import AStart

# 1. Define a "Trap" Graph
# Start -> Trap (1) -> Goal (99)  = Total 100
# Start -> Good (10) -> Goal (10) = Total 20
graph = {
    'Start': {'Trap': 1, 'Good': 10},
    'Trap':  {'Goal': 99},
    'Good':  {'Goal': 10},
    'Goal':  {}
}

solver = AStart(graph)

print("--- Final Verification ---")

# Run Standard (k=1)
path_std = solver.solve('Start', 'Goal', k=1)
print(f"Standard Path: {path_std}")

# Run Batch (k=5)
path_batch = solver.solve('Start', 'Goal', k=5)
print(f"Batch Path:    {path_batch}")

if path_batch == ['Start', 'Good', 'Goal']:
    print("✅ SUCCESS: Batch A* avoided the trap and found the optimal path.")
else:
    print("❌ FAILURE: Batch A* took the wrong path!")
