import math
from multiprocessing import Queue
from multiprocessing import Process

import numpy as np
import time

from interface import implements

from factorizer.dixon_random_squares.rsa_dixon_random_squares import factor_from_reduced_matrix, \
    factorize_number_from_primes
from factorizer.rsa_factorizer import rsa_factorizer
from helper.gaussian_elimination import reduced_row_echelon_form
from helper.primes_sieve import primes_sieve


def build_up_congruence_values(c, n, size, B, queue, pad, m):
    Z = [None] * size
    rows_in_factor = [[0] * len(B)] * size
    rows_in_binary_factor = [[0] * len(B)] * size
    j = 0
    i = 0
    while i < size:
        j = j + 1
        Z[i] = math.ceil(math.sqrt(int(j*m+pad) * n)) + c
        number = Z[i] ** 2 % n
        factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, B)
        if factorized_number_row is not None:
            rows_in_factor[i] = factorized_number_row
            rows_in_binary_factor[i] = factorized_binary_number_row
            i = i + 1
    queue.put((Z, rows_in_factor, rows_in_binary_factor))


class rsa_dixon_random_squares_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, test_congruence):
        self.test_congruence = test_congruence
        self.n = n
        self.e = e
        self.m = m
        k = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = np.array(primes_sieve(k), dtype=int)
        print(len(self.B))

    def build_up_test_values_parallel(self, c):
        queue = Queue()
        all_Z = []
        all_rows_in_binary_factor = []
        all_rows_in_factor = []
        size = math.ceil((len(self.B) + 1) / self.m)
        process = [Process(target=build_up_congruence_values, args=(c, self.n, size, self.B, queue, i, self.m)) for i in
                   range(self.m)]
        for t in process:
            t.start()
        for _ in process:
            Z, rows_in_factor, rows_in_binary_factor = queue.get()
            all_Z.extend(Z)
            all_rows_in_factor.extend(rows_in_factor)
            all_rows_in_binary_factor.extend(rows_in_binary_factor)
        return np.array(all_Z, dtype=object), np.array(all_rows_in_factor), np.array(all_rows_in_binary_factor)

    def factorize(self, c=1):
        print("start building up matrices")
        start_time = int(round(time.time() * 1000))
        Z, all_rows_in_factor, all_rows_in_binary_factor = self.build_up_test_values_parallel(c)
        end_time = int(round(time.time() * 1000))
        print("Building: " + str(end_time - start_time))
        print("end building up matrices")
        print("start echelon")
        start_time = int(round(time.time() * 1000))
        matrix, numpivots = reduced_row_echelon_form(all_rows_in_binary_factor.transpose())
        end_time = int(round(time.time() * 1000))
        print("Echelon: " + str(end_time - start_time))
        print("start echelon")
        print("stop echelon")
        start_time = int(round(time.time() * 1000))
        ones = np.array(
            [[index for (index, bit) in enumerate(matrix[i, :]) if bit] for i in reversed(range(numpivots))])
        print("ones")
        p, q = factor_from_reduced_matrix(ones, self.test_congruence, Z, all_rows_in_factor, self.B, self.n)
        end_time = int(round(time.time() * 1000))
        print("Factor: " + str(end_time - start_time))
        if p is not None and q is not None:
            return p, q
        return self.factorize(c + self.m)
