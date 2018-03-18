import unittest

from helper.polynomial_builder import build_poly
import numpy as np


class TestPolynomialBuiler(unittest.TestCase):
    def test_build_poly_1(self):
        result = build_poly([5])
        self.assertTrue(np.alltrue(result == np.array([-1, 5])))

    def test_build_poly_2(self):
        result = build_poly([15, 8])
        self.assertTrue(np.alltrue(result == np.array([1, -23, 120])))


    def test_build_poly_3(self):
        result = build_poly([6, 2, 3])
        self.assertTrue(np.alltrue(result == np.array([-1, 11, -36, 36])))

if __name__ == '__main__':
    unittest.main()
