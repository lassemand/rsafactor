import random

from math import log, sqrt, ceil

from scipy.special import binom

from factorizer.quadratic_sieve.rsa_quadratic_sieve_helper import calculate_B_values, \
    find_polynomials_and_calculate_values, MIN_PRIME_POLYNOMIAL, MAX_PRIME_POLYNOMIAL


def find_a_and_q(factor_base, a_history, p_min_i, p_max_i, s):
    a = None
    while a is None or a in a_history:
        a = 1
        q = []
        for _ in range(s):
            p_i = 0
            while p_i == 0 or p_i in q:
                p_i = random.randint(p_min_i, p_max_i)
            p = factor_base[p_i].p
            a *= p
            q.append(p_i)
    a_history.add(a)
    return q, a


def find_minimum_prime_distance_to_q(factor_base, q):
    if len(factor_base) == 0:
        return 0, 0, 0
    if q < factor_base[0].p:
        return 0, factor_base[0].p, 1
    for i, poly in enumerate(factor_base):
        if poly.p > q:
            if abs(poly.p - q) < abs(factor_base[i - 1].p - q):
                return i, poly.p, 1
            else:
                return i - 1, factor_base[i - 1].p, 1
    return len(factor_base) - 1, factor_base[-1], 1


def find_interval(factor_base, p_min_i, p_max_i, total_sum, elements_count, u, s, q):
    while elements_count < s or (u ** 2 - u) / (2 * binom(elements_count, s)) >= 1:
        if p_min_i == 0 and p_max_i == len(factor_base):
            break
        if p_min_i == 0 or (total_sum / elements_count < q and p_max_i != len(factor_base)):
            p_max_i += 1
            total_sum += factor_base[p_max_i].p
        else:
            p_min_i -= 1
            total_sum += factor_base[p_min_i].p
        elements_count += 1
    return p_min_i, p_max_i


def calculate_limit_fixed(n, m, factor_base):
    s_hat = round(log(sqrt(2 * n) / m) / log((MAX_PRIME_POLYNOMIAL - MIN_PRIME_POLYNOMIAL) / 2))
    q_hat = 2 ** (0.5 / s_hat) * (sqrt(n) / m) ** (1 / s_hat)
    if q_hat > factor_base[round(len(factor_base) * 0.9)].p:
        s_hat = s_hat + 1
        q_hat = (2 ** (0.5 / s_hat)) * ((sqrt(n) / m) ** (1 / s_hat))
    start, total_sum, elements_count = find_minimum_prime_distance_to_q(factor_base, q_hat)
    k = ceil(log(n, 2))
    u = len(factor_base) / (131987900 * (k ** -3.671828))
    p_min_i, p_max_i = find_interval(factor_base, start, start, total_sum, elements_count, u, s_hat, q_hat)
    return s_hat, p_min_i, p_max_i


class rsa_quadratic_sieve_B_from_fixed:
    def __init__(self, n, m, factor_base):
        self.n = n
        self.m = m
        self.factor_base = factor_base
        self.a_history = set()
        self.s, self.p_min_i, self.p_max_i = calculate_limit_fixed(n, m, factor_base)

    def build(self):
        q, a = find_a_and_q(self.factor_base, self.a_history, self.p_min_i, self.p_max_i, self.s)
        B = calculate_B_values(q, a, self.factor_base)
        g, h = find_polynomials_and_calculate_values(sum(B) % a, a, self.n, self.factor_base, True)
        return g, h, B
