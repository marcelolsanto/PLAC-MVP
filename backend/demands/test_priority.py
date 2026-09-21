import unittest
from .services import calculate_priority

class PriorityCalculationTest(unittest.TestCase):
    def test_minimum_score(self):
        # 1*30 + 1*30 + 1*25 + 1*15 = 100
        score, level = calculate_priority(1, 1, 1, 1)
        self.assertEqual(score, 100)
        self.assertEqual(level, 'BAIXO')

    def test_maximum_score(self):
        # 5*30 + 5*30 + 5*25 + 5*15 = 500
        score, level = calculate_priority(5, 5, 5, 5)
        self.assertEqual(score, 500)
        self.assertEqual(level, 'ALTO')

    def test_medium_score(self):
        # 3*30 + 3*30 + 3*25 + 3*15 = 300
        score, level = calculate_priority(3, 3, 3, 3)
        self.assertEqual(score, 300)
        self.assertEqual(level, 'MEDIO')

    def test_invalid_score_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_priority(2, 3, 3, 3)  # 2 não é permitido
