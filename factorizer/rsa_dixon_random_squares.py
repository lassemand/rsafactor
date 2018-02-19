import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from helper.gaussian_elimination import reduced_row_echelon_form
from helper.primes_sieve import primes_sieve


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


def find_next_selection(row_ones, pointers):
    if pointers is None or len(pointers) == 0 or pointers[0] == -1:
        return None
    temp_pointers = list(pointers)
    i = 0
    while i != len(pointers):
        is_in_the_begining_and_should_update = i == 0 and pointers[i] == len(row_ones) - 1
        is_not_in_the_begining_and_should_update = pointers[i - 1] == pointers[i] + 1
        if is_in_the_begining_and_should_update or is_not_in_the_begining_and_should_update:
            i += 1
            continue
        pointers[i] += 1
        for index in reversed(range(i)):
            pointers[index] = pointers[index + 1] + 1
        return row_ones[temp_pointers]
    pointers[0] = -1
    return row_ones[temp_pointers]


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e
        k = int(math.exp(math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = np.array(primes_sieve(k))
        self.Z = np.array([None] * (len(self.B) + 4))
        self.all_rows_in_factor = [None] * (len(self.B) + 4)
        self.all_rows_in_binary_factor = [None] * (len(self.B) + 4)

    def test_congruences(self, forced_ones):
        list_z_values = list(forced_ones)
        z_congruence = np.prod(self.Z[list_z_values]) % self.n
        y_values = self.B[1:] ** (np.sum(self.all_rows_in_factor[:, 1:][list_z_values, :], axis=0) / 2)
        y_congruence = int(np.prod(y_values)) % self.n
        p = math.gcd(z_congruence + y_congruence, self.n)
        if p != 1 and p != self.n:
            return p, int(self.n / p)
        return None, None

    def factor_from_reduced_matrix(self, ones, current_index=0, forced_zeros=set(), forced_ones=set()):
        if current_index == len(ones):
            return self.test_congruences(forced_ones)
        row_ones = np.array(ones[current_index])
        ones_disjoint = np.array([one for one in row_ones if one not in forced_ones and one not in forced_zeros])
        ones_intersect = forced_ones.intersection(row_ones)
        for d in reversed(range(0, len(ones_disjoint) + len(ones_intersect) + 1, 2)):
            pointers = [i for i in reversed(range(d - len(ones_intersect)))]
            current_selection = find_next_selection(ones_disjoint, pointers)
            while current_selection is not None:
                difference_zeros = set(row_ones).difference(current_selection).difference(ones_intersect)
                new_forced_zeros = forced_zeros.union(difference_zeros)
                new_forced_ones = forced_ones.union(current_selection)
                p, q = self.factor_from_reduced_matrix(ones, current_index + 1, new_forced_zeros, new_forced_ones)
                if p is not None and q is not None:
                    return p, q
                current_selection = find_next_selection(row_ones, pointers)
        if len(ones_intersect) & 1 == 0:
            return self.factor_from_reduced_matrix(ones, current_index + 1, forced_zeros.union(ones_disjoint), forced_ones)
        else:
            return None, None

    def factorize(self, c=0):
        j = 0
        i = 0
        while i < len(self.B) + 4:
            j = j + 1
            if j & 1:
                self.Z[i] = math.floor(math.sqrt(((j + 1) / 2) * self.n)) - c
                should_negate_z_value = [1]
            else:
                self.Z[i] = math.ceil(math.sqrt((j / 2) * self.n)) + c
                should_negate_z_value = [0]
            number = self.Z[i] ** 2 % self.n
            if should_negate_z_value[0]:
                number = (number * -1) % self.n
            factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, self.B, self.n)
            if factorized_number_row is not None:
                self.all_rows_in_binary_factor[i] = should_negate_z_value + factorized_binary_number_row
                self.all_rows_in_factor[i] = should_negate_z_value + factorized_number_row
                i = i + 1
        self.all_rows_in_binary_factor, self.all_rows_in_factor = np.array(self.all_rows_in_binary_factor), np.array(
            self.all_rows_in_factor)
        matrix, numpivots = reduced_row_echelon_form(self.all_rows_in_binary_factor.transpose())
        self.B = np.insert(self.B, 0, -1)
        ones = np.array(
            [[index for (index, bit) in enumerate(matrix[i, :]) if bit] for i in reversed(range(numpivots))])
        p, q = self.factor_from_reduced_matrix(ones)
        if p is not None and q is not None:
            return p, q
        return self.factorize(c + 1)
