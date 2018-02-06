import math
from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_pollard_rho(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def pollard_rho(self, seed=2, f=lambda x: x ** 2 + 1):
        x, y, p = seed, seed, 1
        while p == 1:
            x = f(x) % self.n
            y = f(f(x)) % self.n
            p = math.gcd((x - y) % self.n, self.n)
        return None if p == self.n else p, int(self.n / p)

    def factorize(self):
        X = [2]
        for (_, item) in enumerate(X):
            result = self.pollard_rho(item)
            if result is not None:
                return result
        return None

