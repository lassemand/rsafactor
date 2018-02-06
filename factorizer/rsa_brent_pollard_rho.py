import math
import random

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_brent_pollard_rho(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self):
        y, c, m = random.randint(1, self.n - 1), random.randint(1, self.n - 1), random.randint(1, self.n - 1)
        g, r, q = 1, 1, 1
        while g == 1:
            x = y
            for i in range(r):
                y = ((y * y) % self.n + c) % self.n
            k = 0
            while k < r and g == 1:
                ys = y
                for i in range(min(m, r - k)):
                    y = ((y * y) % self.n + c) % self.n
                    q = q * (abs(x - y)) % self.n
                g = math.gcd(q, self.n)
                k = k + m
            r *= 2
        if g == self.n:
            while True:
                ys = ((ys * ys) % self.n + c) % self.n
                g = math.gcd(abs(x - ys), self.n)
                if g > 1:
                    break

        return g, int(self.n/g)
