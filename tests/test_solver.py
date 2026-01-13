import unittest
from astart import AStart

class TestAStart(unittest.TestCase):
    def test_simple_path(self):
        # A -> B -> C
        graph = {
            'A': {'B': 1},
            'B': {'C': 2},
            'C': {}
        }
        solver = AStart(graph)
        path = solver.solve('A', 'C', k=2)
        self.assertEqual(path, ['A', 'B', 'C'])

    def test_branching_path(self):
        # A -> B (1) -> D (5)
        # A -> C (2) -> D (1)
        # Optimal: A->C->D (Cost 3) vs A->B->D (Cost 6)
        graph = {
            'A': {'B': 1, 'C': 2},
            'B': {'D': 5},
            'C': {'D': 1},
            'D': {}
        }
        solver = AStart(graph)
        path = solver.solve('A', 'D', k=2)
        self.assertEqual(path, ['A', 'C', 'D'])

    def test_no_path(self):
        graph = {
            'A': {'B': 1},
            'C': {}
        }
        solver = AStart(graph)
        path = solver.solve('A', 'C', k=2)
        self.assertIsNone(path)

    def test_internal_goal(self):
        # Goal is reached within the first batch (depth < k)
        # A -> B -> C. k=10.
        graph = {
            'A': {'B': 1},
            'B': {'C': 1},
            'C': {}
        }
        solver = AStart(graph)
        path = solver.solve('A', 'C', k=10)
        self.assertEqual(path, ['A', 'B', 'C'])

if __name__ == '__main__':
    unittest.main()
