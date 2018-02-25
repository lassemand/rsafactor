import unittest

from interface import implements

from factorizer.pollard_rho.k_calculator import k_calculator
from factorizer.pollard_rho.n_calculator import n_calculator
from factorizer.pollard_rho.rsa_pollard_rho_parallel import rsa_pollard_rho_parallel


class rsa_pollard_rho_parallel_test(unittest.TestCase):
    def test_factorizer(self):
        sut = rsa_pollard_rho_parallel(8932919, 1, 3, basic_k_calculator(), basic_n_calculator())
        p, q = sut.factorize()
        if p == 3259:
            p, q = 2741, 3259
        return p, q


if __name__ == '__main__':
    unittest.main()


class basic_k_calculator(implements(k_calculator)):
    def calculate(self, n):
        return 10


class basic_n_calculator(implements(n_calculator)):
    def calculate(self, n, m, k):
        return 4
