import unittest

from factorizer.quadratic_sieve.matrix_operations import build_index_matrix, solve_matrix_opt
from factorizer.quadratic_sieve.rsa_quadratic_sieve import partial_relation_to_full_relation, \
    subtract_partial_relation_exponents
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

    def test_convert_partial_relation_to_full_relation(self):
        partial_relation_exponent_1 = [(0, 1), (11, 1), (23, 1), (38, 1), (43, 1), (44, 1), (49, 1)]
        partial_relation_exponent_2= [(0, 1), (2, 1), (9, 1), (11, 1), (29, 1), (38, 1), (43, 1), (45, 1)]
        result = subtract_partial_relation_exponents(partial_relation_exponent_1, partial_relation_exponent_2)
        self.assertEqual(7, len(result))
        self.assertEqual((2, -1), result[0])
        self.assertEqual((9, -1), result[1])
        self.assertEqual((23, 1), result[2])
        self.assertEqual((29, -1), result[3])
        self.assertEqual((44, 1), result[4])
        self.assertEqual((45, -1), result[5])
        self.assertEqual((49, 1), result[6])

    def test_partial_relation_to_full_relation(self):
        partial_relation = (4026339831, [(2, 1), (23, 1), (29, 1), (137, 1), (229, 1), (233, 1), (401, 1), (521, 1)])
        inversed_partial_relation = (793568979575675827, [(2, 1), (3, 1), (5, 1), (31, 1), (239, 1), (257, 1), (389, 1), (401, 1), (521, 1)])
        u, v, exponents = partial_relation_to_full_relation(partial_relation, inversed_partial_relation, 12163344771174450199)
        self.assertEqual(8261772287037029561, u)
        self.assertEqual(438740304312379483, v)
        self.assertEqual(11, len(exponents))
        self.assertEqual((3, -1), exponents[0])
        self.assertEqual((23, 1), exponents[2])

if __name__ == '__main__':
    unittest.main()
