from interface import implements

from factorizer.pollard_rho.rsa_pollard_rho import rsa_pollard_rho
from factorizer.rsa_factorizer import rsa_factorizer


class rsa_pollard_rho_parallel_independent(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self):
        fac = rsa_pollard_rho(self.n, self.e)
        p, q = fac.factorize()
        return p, q

