import math
import random

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_pollard_rho(implements(rsa_factorizer)):
    def __init__(self, n, e, i=-1):
        self.n = n
        self.e = e
        self.i = i

    def factorize(self, f = lambda u: u ** 2 + 1):
        x = random.randint(2, self.n - 1)
        y = x % self.n
        p = 1
        while p == 1:
            x = f(x) % self.n
            y = f(f(y)) % self.n
            p = math.gcd((x - y) % self.n, self.n)
            if p == self.n:
                return self.factorize(f)
        return p, int(self.n / p)

