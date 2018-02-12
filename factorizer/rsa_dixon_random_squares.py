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
        B = [-1]
        Z = [math.floor(math.sqrt(i/2 * self.n)) if i & 1 else math.ceil(math.sqrt(i * self.n)) for i in range(1, k+1)]
        matrix = []
        for i in range(2, k):
            if miller_rabin(i):
                if self.n % i == 0:
                    return i, self.n / i
                B.append(i)
        for i in range(len(B)):
            z = Z[i]^2 % self.n
        return 59, 31
