import math
import random

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_brent_pollard_rho(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self, f = lambda u: u ** 2 + 1):
        y, c, m = random.randint(1, self.n - 1), random.randint(1, self.n - 1), random.randint(1, self.n - 1)
        p, r, q = 1, 1, 1
        while p == 1:
            x = y
            for i in range(r):
                y = f(y) % self.n
            k = 0
            while k < r and p == 1:
                ys = y
                for i in range(min(m, r - k)):
                    y = f(y) % self.n
                    q = q * (abs(x - y)) % self.n
                p = math.gcd(q, self.n)
                k = k + m
            r *= 2
        if p == self.n:
            while True:
                ys = f(ys) % self.n
                p = math.gcd(abs(x - ys), self.n)
                if p > 1:
                    break

        return p, int(self.n / p)

if __name__ == "__main__":
    factorizer =  rsa_brent_pollard_rho(21)
    factorizer.factorize()
