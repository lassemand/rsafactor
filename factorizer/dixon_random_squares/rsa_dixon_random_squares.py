import math
import numpy as np

from interface import implements, Interface

from factorizer.rsa_factorizer import rsa_factorizer
from helper.gaussian_elimination import reduced_row_echelon_form
from helper.primes_sieve import primes_sieve


def factorize_number_from_primes(number, primes, n):
    factorized_number_binary_row = [0] * (len(primes))
    factorized_number_row = [0] * (len(primes))
    list_of_factors = []
    current_factor_value = 1
    for (index, prime) in enumerate(primes):
        value = 1
        while number % (prime ** value) == 0:
            value += 1
        exponent = value - 1
        factorized_number_row[index] = exponent
        if exponent != 0:
            list_of_factors.append(number ** exponent)
            factorized_number_binary_row[index] = exponent & 1 if number % prime == 0 else 0
            current_factor_value = current_factor_value * (prime.item() ** exponent)
            if current_factor_value == number:
                return factorized_number_binary_row, factorized_number_row
    return None, None


def find_next_selection(row_ones, pointers):
    if pointers is None or len(pointers) == 0:
        return [], None
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
        return row_ones[temp_pointers], pointers
    return row_ones[temp_pointers], None


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e, test_congruence):
        self.test_congruence = test_congruence
        self.n = n
        self.e = e
        k = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = np.array(primes_sieve(k), dtype=int)
        print(len(self.B))


    def factor_from_reduced_matrix(self, ones):
        p, q = None, None
        current_index = 0
        forced_zeros = set()
        reduced_ones = []
        for one in ones:
            if len(one) == 1:
                forced_zeros.add(one[0])
            else:
                reduced_ones.append(one)
        ones = reduced_ones
        states = [[set(), set(), None, False] for i in range(len(ones) + 1)]
        states[0][0] = forced_zeros
        while p is None and q is None:
            if current_index == -1:
                return None, None
            if current_index == len(ones):
                return self.test_congruence.validate(states[current_index][1], self.Z, self.all_rows_in_factor, self.B, self.n)
            if not states[current_index][3]:
                row_ones = np.array(ones[current_index])
                ones_disjoint = np.array([one for one in row_ones if
                                      one not in states[current_index][1] and one not in states[current_index][0]])
                ones_intersect = states[current_index][1].intersection(row_ones)
                pointers = states[current_index][2]
                if pointers is None:
                    d = len(ones_disjoint) - 1 if len(ones_disjoint) & 1 else len(ones_disjoint)
                    if len(ones_intersect) & 1:
                        d += 1
                    if d > len(ones_disjoint):
                        d -= 2
                    pointers = [i for i in reversed(range(d))]
                current_selection, pointers = find_next_selection(ones_disjoint, pointers)
                if pointers is None:
                    if current_selection is None or len(current_selection) - 2 <= 0:
                        states[current_index][3] = True
                    else:
                        pointers = [i for i in reversed(range(len(current_selection) - 2))]
                states[current_index][2] = pointers
                difference_zeros = set(row_ones).difference(current_selection).difference(ones_intersect)
                new_forced_zeros = states[current_index][0].union(difference_zeros)
                new_forced_ones = states[current_index][1].union(current_selection)
                current_index += 1
                states[current_index][0] = new_forced_zeros
                states[current_index][1] = new_forced_ones
                states[current_index][3] = False
                continue
            current_index -= 1
        return p, q

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
            factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, self.B, self.n)
            if factorized_number_row is not None:
                all_rows_in_binary_factor[i] = factorized_binary_number_row
                all_rows_in_factor[i] = factorized_number_row
                i = i + 1
        return Z, np.array(all_rows_in_binary_factor), np.array(all_rows_in_factor)

    def factorize(self, c=0):
        print("start building up matrices")
        self.Z, self.all_rows_in_binary_factor, self.all_rows_in_factor = self.build_up_test_values(c)
        print("end building up matrices")
        print("start echelon")
        matrix, numpivots = reduced_row_echelon_form(self.all_rows_in_binary_factor.transpose())
        print("stop echelon")
        ones = np.array(
            [[index for (index, bit) in enumerate(matrix[i, :]) if bit] for i in reversed(range(numpivots))])
        print("ones")
        p, q = self.factor_from_reduced_matrix(ones)
        if p is not None and q is not None:
            return p, q
        return self.factorize(c + 1)


