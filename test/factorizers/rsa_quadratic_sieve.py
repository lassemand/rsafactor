import unittest

from factorizer.quadratic_sieve.matrix_operations import build_index_matrix, solve_matrix_opt
from helper.cryptographic_methods import sqrt_int, modular_square_root


class TestQuadraticSieve(unittest.TestCase):
    def test_sqrt(self):
        value = sqrt_int(17)
        self.assertEqual(4, value)

    def test_sqrt_mod_prime(self):
        result = modular_square_root(72, 607)
        self.assertEqual(50, result)

    def test_build_index_matrix(self):
        result = build_index_matrix([[0, 1, 1, 0],[1, 0, 1, 1], [0, 0, 1, 1]])
        self.assertEqual([2, 1, 7, 6], result[0])

    def test_build_index_matrix(self):
        result = build_index_matrix([[0, 1, 1, 0],[1, 0, 1, 1], [0, 0, 1, 1]])
        self.assertEqual([2, 1, 7, 6], result[0])

    def test_solve_matrix_opt(self):
        M_opt, M_n, M_m = build_index_matrix([[1, 1, 0, 1, 1], [1, 0, 1, 0, 1], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]])
        perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
        self.assertEqual([0, 1, 4], perfect_squares[0])

if __name__ == '__main__':
    unittest.main()
