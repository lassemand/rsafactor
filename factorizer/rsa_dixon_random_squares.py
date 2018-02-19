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


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e
        k = int(math.exp(math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = np.array(primes_sieve(k))
        self.Z = np.array([None] * (len(self.B) + 4))
        self.all_rows_in_factor = [None] * (len(self.B) + 4)
        self.all_rows_in_binary_factor = [None] * (len(self.B) + 4)

    def test_congruences(self, forced_ones, Z, all_rows_in_factor, n, B):
        list_z_values = list(forced_ones)
        z_congruence = np.prod(Z[list_z_values]) % n
        y_values = B[1:] ** (np.sum(all_rows_in_factor[:, 1:][list_z_values, :], axis=0) / 2)
        y_congruence = int(np.prod(y_values)) % n
        p = math.gcd(z_congruence + y_congruence, n)
        if p != 1 and p != n:
            return p, int(n / p)
        return None, None

    def find_factor_from_all_possibilites(self, d, row_ones, ones, Z, all_rows_in_factor, B, n, current_index,
                                          forced_zeros,
                                          forced_ones):
        pointers = [i for i in reversed(range(d))]
        while i != len(pointers):
            is_in_the_begining_and_should_update = i == 0 and pointers[i] == len(row_ones) - 1
            is_not_in_the_begining_and_should_update = pointers[i - 1] == pointers[i] + 1
            if is_in_the_begining_and_should_update or is_not_in_the_begining_and_should_update:
                i += 1
                continue
            pointers[i] += 1
            for index in reversed(range(i)):
                pointers[index] = pointers[index + 1] + 1
            current_selection = row_ones[pointers]
            p, q = self.factor_from_reduced_matrix(ones, Z, all_rows_in_factor, B, n, current_index + 1,
                                                   forced_zeros + row_ones[np.setdiff1d(row_ones, current_selection)],
                                                   forced_ones + current_selection)
            if p is not None and q is not None:
                return p, q
            i = 0
        return None, None

    def factor_from_reduced_matrix(self, ones, Z, all_rows_in_factor, B, n, current_index=0, forced_zeros=set(),
                                   forced_ones=set()):
        if current_index == len(ones):
            return self.test_congruences(forced_ones, Z, all_rows_in_factor, n, B)
        row_ones = ones[current_index]

        ones_disjoint = [one for one in row_ones if one not in forced_ones and one not in forced_zeros]
        for d in reversed(range(0, len(ones_disjoint) + 1, 2)):
            p, q = self.factor_from_reduced_matrix(ones, Z, all_rows_in_factor, B, n, current_index + 1,
                                                   forced_zeros.union(set(ones_disjoint[d:])),
                                                   forced_ones.union(set(ones_disjoint[:d])))
            if p is not None and q is not None:
                return p, q
            p, q = self.find_factor_from_all_possibilites(d, row_ones, Z, all_rows_in_factor, B, n, current_index,
                                                          forced_zeros,
                                                          forced_ones)
            if p is not None and q is not None:
                return p, q
        return None, None

    def dixon(self, c=0):
        j = 0
        i = 0
        while i < len(self.B) + 4:
            j = j + 1
            if j & 1:
                Z[i] = math.floor(math.sqrt(((j + 1) / 2) * self.n)) - c
                should_negate_z_value = [1]
            else:
                Z[i] = math.ceil(math.sqrt((j / 2) * self.n)) + c
                should_negate_z_value = [0]
            number = Z[i] ** 2 % self.n
            if should_negate_z_value[0]:
                number = (number * -1) % self.n
            factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, B, self.n)
            if factorized_number_row is not None:
                all_rows_in_binary_factor[i] = should_negate_z_value + factorized_binary_number_row
                all_rows_in_factor[i] = should_negate_z_value + factorized_number_row
                i = i + 1
        all_rows_in_binary_factor, all_rows_in_factor = np.array(all_rows_in_binary_factor), np.array(
            all_rows_in_factor)
        matrix, numpivots = reduced_row_echelon_form(all_rows_in_binary_factor.transpose())
        # I add this element now because it makes the factoring easier not to have it from the beginning
        B = np.insert(B, 0, -1)
        ones = np.array(
            [[index for (index, bit) in enumerate(matrix[i, :]) if bit] for i in reversed(range(numpivots))])
        p, q = factor_from_reduced_matrix(ones, Z, all_rows_in_factor, B, self.n)
        if p is not None and q is not None:
            return p, q
        return self.dixon(B, c + 1)

    def factorize(self):
        return self.dixon()
