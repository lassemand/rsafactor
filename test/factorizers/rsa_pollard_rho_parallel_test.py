import unittest

from interface import implements
import numpy as np

from factorizer.pollard_rho.k_calculator import k_calculator
from factorizer.pollard_rho.n_calculator import n_calculator

from factorizer.pollard_rho.rsa_pollard_rho_parallel_worker import correlation_product, compute_values, build_poly, \
    polyval


class rsa_pollard_rho_parallel_test(unittest.TestCase):

    def test_pollard_rho_parallel(self):
        xs = np.array([[4,3], [5,2]])
        ys = np.array([[7,6], [7,6]])
        Q = correlation_product(xs, ys)
        self.assertEqual(2880, Q)


    def test_compute_values(self):
        n = 10
        X, Y = compute_values(4, n, 1, 1)
        self.assertEqual(X[1], Y[0])
        self.assertEqual(X[3], Y[1])

    def test_pollard_rho_parallel_simpler(self):
        x = [4,3]
        y = [7,6]
        polynomial = build_poly(y)
        Q = 1
        for value in x:
            Q *= polyval(polynomial, value)
        self.assertEqual(72, Q)

    def test_compute_values_with_real_example(self):
        y = [1490270837, 202440493, 548430952]
        x = [1921262042, 210102397, 1042596808]
        polynomial = build_poly(y)
        Q = 1
        for value in x:
            Q *= polyval(polynomial, value)
        self.assertEqual(627268546860890928494651012960094402904568879547143191107700437527350502400000, Q)


if __name__ == '__main__':
    unittest.main()

