import math
import numpy as np
import time

from interface import implements

from factorizer.quadratic_sieve.matrix_operations import build_index_matrix, solve_matrix_opt
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import sqrt_int
from helper.primes_sieve import primes_sieve


def factorize_number_from_primes(number, primes):
    factorized_number_binary_row = [0] * (len(primes))
    a = number
    for (index, prime) in enumerate(primes):
        exp = 0
        while a % prime == 0:
            a //= prime
            exp += 1
        factorized_number_binary_row[index] = exp % 2
        if a == 1:
            return factorized_number_binary_row
    return None


def factor_from_square(n, square_indices, smooth_relations):
    res = [1, 1]
    for idx in square_indices:
        res[0] *= smooth_relations[idx][0]
        res[1] *= smooth_relations[idx][1]
    res[1] = sqrt_int(res[1])
    return math.gcd(res[0] + res[1], n)


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e, test_congruence):
        self.test_congruence = test_congruence
        self.n = n
        self.e = e
        k = int(math.exp(0.4 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = primes_sieve(k)

    def find_smooth_relations(self, c, stop_factor, j, smooth_relations, binary_matrix):
        stop_condition = math.ceil(len(self.B) * stop_factor)
        while len(smooth_relations) < stop_condition:
            j = j + 1
            Z = math.ceil(math.sqrt(j * self.n)) + c
            Z_squared = int(Z ** 2 % self.n)
            factorized_binary_number_row = factorize_number_from_primes(Z_squared, self.B)
            if factorized_binary_number_row is not None:
                smooth_relations.append((Z, Z_squared))
                binary_matrix.append(factorized_binary_number_row)
        return smooth_relations, binary_matrix, j

    def factorize(self, c=1):
        stop_factor = 1.00
        p = 1
        j = 0
        smooth_relations = []
        binary_matrix = []
        while p == 1 or p == self.n:
            stop_factor += 0.02
            smooth_relations, binary_matrix, j = self.find_smooth_relations(c, stop_factor, j, smooth_relations, binary_matrix)
            M_opt, M_n, M_m = build_index_matrix(binary_matrix)
            perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
            print("Done")
            for square_indices in perfect_squares:
                p = factor_from_square(self.n, square_indices, smooth_relations)
                if p != 1 and p != self.n:
                    break
        return p, int(self.n / p)
