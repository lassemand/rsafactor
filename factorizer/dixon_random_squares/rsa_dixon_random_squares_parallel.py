from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_dixon_random_squares_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, test_congruence):
        self.n = n
        self.e = e


    def factorize(self, c=1):
        return 1, 1
