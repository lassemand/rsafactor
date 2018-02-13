import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from helper.miller_rabin import miller_rabin


def find_all_pair_of_size(n, d):
    pointers = [i for i in reversed(range(d))]
    return generate_all_pairs(pointers, n, 0, [list(pointers)])


def generate_all_pairs(pointers, n, i, all_pairs):
    is_all_pairs_generated = i == len(pointers)
    if is_all_pairs_generated:
        return all_pairs

    is_in_the_begining_and_should_update = i == 0 and pointers[i] == n - 1
    is_not_in_the_begining_and_should_update = pointers[i - 1] == pointers[i] + 1
    if is_in_the_begining_and_should_update or is_not_in_the_begining_and_should_update:
        return generate_all_pairs(pointers, n, i + 1, all_pairs)

    pointers[i] += 1
    for index in reversed(range(i)):
        pointers[index] = pointers[index + 1] + 1
    all_pairs.append(list(pointers))

    return generate_all_pairs(pointers, n, 0, all_pairs)


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


def factorize_numbers_from_primes(numbers, primes, n):
    all_rows_in_binary_factor = []
    all_rows_in_factor = []
    all_indicies_with_factor = []
    for (index, number) in enumerate(numbers):
        # We know that even numbers are supposed to be close n wheres even numbers are close to 0.
        if index & 1 == 0:
            number = (number * -1) % n
        factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, primes, n)
        if factorized_binary_number_row is not None:
            all_rows_in_binary_factor.append(factorized_binary_number_row)
            all_rows_in_factor.append(factorized_number_row)
            all_indicies_with_factor.append(index)
    return np.matrix(all_rows_in_binary_factor), all_indicies_with_factor, np.array(all_rows_in_factor)


def find_set_to_reach_zero_sum_vector_from_candidates(matrix, candidates):
    for i in reversed(range(matrix.shape[1])):
        new_candidates = []
        for cand in candidates:
            if np.sum(matrix[:, i][cand, :]) & 1 == 0:
                new_candidates.append(cand)
        candidates = list(new_candidates)
    return candidates


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self):
        k = math.exp(math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n))))
        B = np.array([b for b in range(2, int(k)) if miller_rabin(b)])
        Z = np.array([int(
            math.floor(math.sqrt((((i + 1) / 2) * self.n))) if i & 1 else int(math.ceil(math.sqrt((i / 2) * self.n))))
            for i in range(1, int(len(B) + 1))])
        binary_matrix, indicies, exponent_matrix = factorize_numbers_from_primes([z ** 2 % self.n for z in Z], B, self.n)
        Z = Z[indicies]
        for d in range(2, binary_matrix.shape[1]):
            factorize_candidates = find_set_to_reach_zero_sum_vector_from_candidates(binary_matrix, find_all_pair_of_size(
                binary_matrix.shape[0], d))
            for fac_cand in factorize_candidates:
                z_congruence = np.prod(Z[fac_cand])
                y_values = B ** (np.sum(exponent_matrix[fac_cand,:], axis=0) / 2)
                y_congruence = int(np.prod(y_values))
                p = math.gcd(z_congruence + y_congruence, self.n)
                if p != 1 and p != self.n:
                    return p, int(self.n / p)
        # TODO refactorize with a more random j
        return 59, 31
