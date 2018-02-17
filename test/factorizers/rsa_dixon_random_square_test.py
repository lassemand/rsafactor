import unittest
import numpy as np

from factorizer.rsa_dixon_random_squares import find_ones, generate_candidates_from_ones, generate_all_pairs, \
    rsa_dixon_random_squares, generate_disjoint_and_intersection


class rsa_dixon_random_square_test(unittest.TestCase):
    def test_zero_sum_vector_candidates(self):
        matrix = np.array([[1, 0, 0, 0, 1, 0],
                           [0, 1, 0, 0, 1, 1],
                           [0, 0, 1, 0, 1, 0],
                           [0, 0, 0, 1, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           ])
        allowed_ones = find_ones(matrix, 4)
        self.assertCountEqual(allowed_ones, [[2, 4], [1, 4, 5], [0, 4]])

    def test_generate_candidates_from_ones(self):
        candidates = generate_candidates_from_ones(np.array([[2, 4], [1, 4, 5], [0, 4]]))
        self.assertEqual(3, len(candidates))

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(1829, 1)
        (p, q) = sut.factorize()
        if p == 59:
            p, q = 31, 59
        self.assertEqual(p, 31)
        self.assertEqual(q, 59)

    def test_generate_disjoint_and_intersection(self):
        intersection, disjoint = generate_disjoint_and_intersection([3], [1,2], [0,2,3])
        self.assertEqual(1, len(intersection))
        self.assertEqual(2, intersection[0])
        self.assertEqual(1, len(disjoint))
        self.assertEqual(0, disjoint[0])

if __name__ == '__main__':
    unittest.main()
