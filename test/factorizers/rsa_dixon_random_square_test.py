import unittest
import numpy as np

from factorizer.rsa_dixon_random_squares import find_ones


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
        allowed_ones, disallowed_ones = find_ones(matrix.transpose())

if __name__ == '__main__':
    unittest.main()
