import random
from math import sqrt

from factorizer.quadratic_sieve.rsa_quadratic_sieve_helper import calculate_B_values, \
    find_polynomials_and_calculate_values

NUMBER_OF_RETRIES_FINDING_A = 20


def find_a_and_q(n, m, factor_base, p_min_i, p_max_i):
    target = sqrt(2 * float(n)) / m
    target1 = target / ((factor_base[p_min_i].p +
                         factor_base[p_max_i].p) / 2) ** 0.5
    best_q, best_a, best_ratio = None, None, None
    for _ in range(NUMBER_OF_RETRIES_FINDING_A):
        a = 1
        q = []

        while a < target1:
            p_i = 0
            while p_i == 0 or p_i in q:
                p_i = random.randint(p_min_i, p_max_i)
            p = factor_base[p_i].p
            a *= p
            q.append(p_i)

        ratio = abs((a / target) - 1)

        if best_ratio is None or ratio < best_ratio:
            best_q = q
            best_a = a
            best_ratio = ratio
    return best_q, best_a


class rsa_quadratic_sieve_B_from_variable:
    def __init__(self, n, m, factor_base, p_min_i, p_max_i):
        self.n = n
        self.m = m
        self.factor_base = factor_base
        self.p_min_i = p_min_i
        self.p_max_i = p_max_i

    def build(self):
        q, a = find_a_and_q(self.n, self.m, self.factor_base, self.p_min_i, self.p_max_i)
        B = calculate_B_values(q, a, self.factor_base)
        g, h = find_polynomials_and_calculate_values(sum(B) % a, a, self.n, self.factor_base, True)
        return g, h, B
