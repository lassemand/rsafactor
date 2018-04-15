import math
import numpy as np
import time

from interface import implements, Interface

from factorizer.quadratic_sieve.matrix_operations import build_index_matrix, solve_matrix_opt
from factorizer.rsa_factorizer import rsa_factorizer
from helper.primes_sieve import primes_sieve


def factorize_number_from_primes(number, primes):
    factorized_number_binary_row = [0] * (len(primes))
    factorized_number_row = [0] * (len(primes))
    a = number
    for (index, prime) in enumerate(primes):
        exp = 0
        while a % prime == 0:
            a //= prime
            exp += 1
        if exp > 0:
            factorized_number_row[index] = exp
            factorized_number_binary_row[index] = exp % 2
        if a == 1:
            return factorized_number_binary_row, factorized_number_row
    return None, None


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e, test_congruence):
        self.test_congruence = test_congruence
        self.n = n
        self.e = e
        k = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = primes_sieve(k)

    def build_up_test_values(self, c):
        Z = np.array([None] * (len(self.B) + 1))
        all_rows_in_factor = [None] * (len(self.B) + 1)
        all_rows_in_binary_factor = [None] * (len(self.B) + 1)
        j = 0
        i = 0
        while i < len(self.B) + 1:
            j = j + 1
            Z[i] = math.ceil(math.sqrt(j * self.n)) + c
            number = Z[i] ** 2 % self.n
            factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, self.B)
            if factorized_number_row is not None:
                all_rows_in_binary_factor[i] = factorized_binary_number_row
                all_rows_in_factor[i] = factorized_number_row
                i = i + 1
        return Z, np.array(all_rows_in_binary_factor), np.array(all_rows_in_factor)

    def factorize(self, c=1):
        print("start building up matrices")
        start_time = int(round(time.time() * 1000))
        Z, all_rows_in_binary_factor, all_rows_in_factor = self.build_up_test_values(c)
        end_time = int(round(time.time() * 1000))
        print("Building: " + str(end_time - start_time))
        print("end building up matrices")
        print("start echelon")
        M_opt, M_n, M_m = build_index_matrix(all_rows_in_binary_factor)
        perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
        for square_indices in perfect_squares:
            p, q = self.test_congruence.validate(square_indices, Z, all_rows_in_factor, self.B, self.n)
            if p is not None and q is not None:
                return p, q

        return self.factorize(c + 1)
