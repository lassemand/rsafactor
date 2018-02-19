import unittest
import numpy as np

from helper.gaussian_elimination import reduced_row_echelon_form


class TestGaussian(unittest.TestCase):
    def test_zero_sum_vector_candidates(self):
        matrix = np.array([[1, 0, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0], [1, 0, 0, 0, 0, 1, 0],
                            [1, 0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 0, 0, 0], ])
        matrix, numpivots = reduced_row_echelon_form(matrix.transpose())
        self.assertTrue(np.alltrue(matrix == np.matrix([[1, 0, 0, 0, 1, 0],
                                                        [0, 1, 0, 0, 1, 1],
                                                        [0, 0, 1, 0, 1, 0],
                                                        [0, 0, 0, 1, 0, 0],
                                                        [0, 0, 0, 0, 0, 0],
                                                        [0, 0, 0, 0, 0, 0],
                                                        [0, 0, 0, 0, 0, 0],
                                                        ])))
        self.assertEqual(4, numpivots)


    def test_21_value_zero_sum_vector(self):
        matrix = np.array([[1, 0, 1, 0, 1, 1, 0, 1],
                           [0, 0, 1, 0, 1, 0, 0, 0],
                           [0, 0, 1, 0, 0, 1, 0, 0],
                           [1, 0, 0, 0, 0, 0, 0, 1],
                           [0, 0, 0, 1, 1, 0, 0, 0], ])
        matrix, numpivots = reduced_row_echelon_form(matrix)
        self.assertTrue(np.alltrue(matrix == np.matrix([[1, 0, 0, 0, 0, 0, 0, 1],
                                                        [0, 0, 1, 0, 0, 0, 0, 0],
                                                        [0, 0, 0, 1, 0, 0, 0, 0],
                                                        [0, 0, 0, 0, 1, 0, 0, 0],
                                                        [0, 0, 0, 0, 0, 1, 0, 0],
                                                        ])))
        self.assertEqual(5, numpivots)

if __name__ == '__main__':
    unittest.main()
