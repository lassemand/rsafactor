import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from helper.gaussian_elimination import reduced_row_echelon_form
from helper.primes_sieve import primes_sieve


def find_all_pair_of_size(n, d):
    pointers = [i for i in reversed(range(d))]
    return generate_all_pairs(pointers, n, 0, [list(pointers)])


def generate_all_pairs(pointers, n, i, all_pairs):
    while i != len(pointers):
        is_in_the_begining_and_should_update = i == 0 and pointers[i] == n - 1
        is_not_in_the_begining_and_should_update = pointers[i - 1] == pointers[i] + 1
        if is_in_the_begining_and_should_update or is_not_in_the_begining_and_should_update:
            i += 1
            continue
        pointers[i] += 1
        for index in reversed(range(i)):
            pointers[index] = pointers[index + 1] + 1
        all_pairs.append(list(pointers))
        i = 0
    return all_pairs


def find_exponent(number, prime, value, n):
    return find_exponent(number, prime, value + 1, n) if number % (prime ** value) == 0 else value - 1


def factorize_number_from_primes(number, primes, n):
    factorized_number_binary_row = [0] * (len(primes))
    factorized_number_row = [0] * (len(primes))
    list_of_factors = []
    current_factor_value = 1
    for (index, prime) in enumerate(primes):
        exponent = find_exponent(number, prime, 1, n)
        factorized_number_row[index] = exponent
        if exponent != 0:
            list_of_factors.append(number ** exponent)
            factorized_number_binary_row[index] = exponent & 1 if number % prime == 0 else 0
            current_factor_value = current_factor_value * (prime ** exponent)
            if current_factor_value == number:
                return factorized_number_binary_row, factorized_number_row
    return None, None


def find_set_to_reach_zero_sum_vector_from_candidates(matrix, candidates):
    for i in reversed(range(matrix.shape[1])):
        new_candidates = []
        current_row = matrix[:, i]
        print(i)
        for cand in candidates:
            if np.sum(current_row[cand, :]) & 1 == 0:
                new_candidates.append(cand)
        candidates = list(new_candidates)
    return candidates


def find_ones(matrix, numpivots):
    disallowed_ones = set()
    allowed_ones = []
    for i in reversed(range(numpivots)):
        result = [index for index, row in enumerate(matrix[i,:]) if row[index] and index not in disallowed_ones]
        if len(result):
            disallowed_ones.add(result[0])
        else:
            allowed_ones.append(result)


def factor_from_reduced_matrix(matrix, numpivots, all_rows_in_factor, Z, B, n):
    allowed_ones, disallowed_ones = find_ones(matrix, numpivots)
    z_congruence = np.prod(Z[fac_cand])
    y_values = B ** (np.sum(all_rows_in_factor[:,1:][fac_cand,:], axis=0) / 2)
    y_congruence = int(np.prod(y_values))
    p = math.gcd(z_congruence + y_congruence, n)
    if p != 1 and p != n:
        return p, int(n / p)



class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def dixon(self, B, c=0):
        j = 0
        i = 0
        Z = np.array([None] * (len(B) + 4))
        all_rows_in_binary_factor = [None] * (len(B) + 4)
        all_rows_in_factor = [None] * (len(B) + 4)
        while i < len(B) + 4:
            j = j + 1
            if j & 1:
                Z[i] = math.floor(math.sqrt(((j+1)/2)*self.n)) - c
                should_negate_z_value = [1]
            else:
                Z[i] = math.ceil(math.sqrt((j/2)*self.n)) + c
                should_negate_z_value = [0]
            number = Z[i] ** 2 % self.n
            if should_negate_z_value[0]:
                number = (number * -1) % self.n
            factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, B, self.n)
            if factorized_number_row is not None:
                all_rows_in_binary_factor[i] = should_negate_z_value + factorized_binary_number_row
                all_rows_in_factor[i] = should_negate_z_value + factorized_number_row
                i = i + 1
        all_rows_in_binary_factor, all_rows_in_factor = np.array(all_rows_in_binary_factor), np.array(all_rows_in_factor)
        matrix, numpivots = reduced_row_echelon_form(all_rows_in_binary_factor)
        p, q = factor_from_reduced_matrix(all_rows_in_binary_factor, numpivots, all_rows_in_factor, Z, B, self.n)
        if p is not None and q is not None:
            return p, q
        return self.dixon(B, c+1)


    def factorize(self):
        k = int(math.exp(math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        B = np.array(primes_sieve(k))
        return self.dixon(B, )







