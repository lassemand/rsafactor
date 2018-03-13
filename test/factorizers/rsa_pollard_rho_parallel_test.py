import unittest

from interface import implements
import numpy as np

from factorizer.pollard_rho.k_calculator import k_calculator
from factorizer.pollard_rho.n_calculator import n_calculator
from factorizer.pollard_rho.rsa_pollard_rho_parallel import rsa_pollard_rho_parallel, compute_values, correlation_product

from multiprocessing import Queue

class rsa_pollard_rho_parallel_test(unittest.TestCase):
    def test_factorizer(self):
        sut = rsa_pollard_rho_parallel(8932919, 1, 1, basic_k_calculator(), basic_n_calculator())
        p, q = sut.factorize()
        if p == 3259:
            p, q = 2741, 3259
        return p, q

    def test_pollard_rho_parallel(self):
        queue = Queue()
        xs = np.array([[4,3], [5,2]])
        ys = np.array([[7,6], [7,6]])
        correlation_product(xs, ys, queue)
        Q = queue.get()
        self.assertEqual(2880, Q)


    def test_compute_values(self):
        queue = Queue()
        n = 10
        compute_values(queue, 4, n, 1, 1)
        X, Y = queue.get()
        self.assertEqual(X[1], Y[0])
        self.assertEqual(X[3], Y[1])


if __name__ == '__main__':
    unittest.main()


class basic_k_calculator(implements(k_calculator)):
    def calculate(self, n):
        return 1


class basic_n_calculator(implements(n_calculator)):
    def calculate(self, n, m, k):
        return 10
