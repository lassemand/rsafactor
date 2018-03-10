import math

import time
from interface import implements

from factorizer.dixon_random_squares.dixon_factor_base_prime import dixon_factor_base_prime
from factorizer.quadratic_sieve.matrix_operations import solve_matrix_opt, build_index_matrix
from factorizer.quadratic_sieve.rsa_quadratic_sieve import trial_divide, siqs_find_factors
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import sqrt_int
from helper.primes_sieve import primes_sieve


def build_binary_matrix(factor_base, smooth_relations):
    """Build the matrix for the linear algebra step of the Quadratic Sieve."""
    fb = len(factor_base)
    M = []
    for sr in smooth_relations:
        mi = [0] * fb
        for j, exp in sr[1]:
            mi[j] = exp % 2
        M.append(mi)
    return M


def siqs_find_factors(n, perfect_squares, smooth_relations, B):
    for square_indices in perfect_squares:
        fact = factor_from_square(n, square_indices, smooth_relations, B)
        if fact != 1 and fact != n:
            print("Found")
            return fact, int(n / fact)
        else:
            print("Not found")
    print("Recalculate")
    return None, None


def calculate_prime_value(B, relations):
    value = 1
    for relation in relations:
        value *= B[relation[0]].p ** relation[1]
    return value

def factor_from_square(n, square_indices, smooth_relations, B):
    y = 1
    z = 1
    for indicies in square_indices:
        smooth_relation = smooth_relations[indicies]
        z *= smooth_relation[0]
        for value in smooth_relation[1]:
            y *= B[value[0]].p ** value[1]
    y = sqrt_int(y) % n
    z = z % n

    return math.gcd(abs(z - y), n)


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e
        k = int(0.5 * math.exp(math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = [dixon_factor_base_prime(p) for p in primes_sieve(k)]

    def build_up_test_values(self, c):
        smooth_relations = []
        j = 0
        while len(smooth_relations) < (len(self.B) + 1):
            j += 1
            z = math.ceil(math.sqrt(j * self.n)) + c
            number = z ** 2 % self.n
            divisors_idx = trial_divide(number, self.B)
            if divisors_idx is not None:
                smooth_relations.append((z, divisors_idx))
        return smooth_relations

    def factorize(self, c=1):
        start_time = int(round(time.time() * 1000))
        smooth_relations = self.build_up_test_values(c)
        end_time = int(round(time.time() * 1000))
        print(end_time - start_time)
        start_time = int(round(time.time() * 1000))
        M = build_binary_matrix(self.B, smooth_relations)
        end_time = int(round(time.time() * 1000))
        print(end_time - start_time)
        M_opt, M_n, M_m = build_index_matrix(M)
        perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
        p, q = siqs_find_factors(self.n, perfect_squares, smooth_relations, self.B)
        if p is not None and q is not None:
            return p, q
        return self.factorize(c + 1)
