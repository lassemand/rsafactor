from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_brute_force(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self):
        counter = 3
        while True:
            if self.n % counter == 0:
                print("Found!")
                return counter, int(self.n / counter)
            counter += 2
