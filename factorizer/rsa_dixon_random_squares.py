import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from helper.miller_rabin import miller_rabin

def find_all_pair_of_size(d, n):
    pointers = [i for i in reversed(range(d))]
    return generate_all_pairs(pointers, n, 0, [tuple(pointers) + (0,)])

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
    all_pairs.append(tuple(pointers) + (0,))
    return generate_all_pairs(pointers, n, 0, all_pairs)


class rsa_dixon_random_squares(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def is_smooth(y, b):
        return True

    def factorize(self):
        # b = math.exp(math.sqrt(math.log10(self.n) * math.log10(math.log10(self.n))))
        b = 13
        B = []
        for i in range(2, b):
            if miller_rabin(i):
                if self.n % i == 0:
                    return i, self.n / i
                B.append(i)
        for i in range(len(B)):
            a = random.randint(1, self.n - 1)
            if math.gcd(a, self.n) != 1:
                return a, int(self.n / a)
            y = a ^ 2 % self.n
            if self.is_smooth(y, b):
                print("test")
        return 59, 31
