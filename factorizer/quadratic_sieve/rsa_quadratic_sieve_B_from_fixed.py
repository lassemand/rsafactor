import random

from math import log, sqrt, ceil

from scipy.stats import binom

from factorizer.quadratic_sieve.rsa_quadratic_sieve_helper import calculate_B_values, \
    find_polynomials_and_calculate_values, MIN_PRIME_POLYNOMIAL, MAX_PRIME_POLYNOMIAL


def find_a_and_q(n, m, factor_base, a_history, p_min_i, p_max_i, q_length):
    a = 1
    q = []
    for _ in range():
        p_i = 0
        while p_i == 0 or p_i in q:
            p_i = random.randint(p_min_i, p_max_i)
        p = factor_base[p_i].p
        a *= p
        q.append(p_i)

    if a in a_history:
        return find_a_and_q(n, m, factor_base, a_history, p_min_i, p_max_i, q_length)
    return q, a


def calc_collision_prop(u, s, x):
    return (u^2 - u) / 2 (binom(x, s))


def redefine_interval_according_to_s(s_hat, n, m, factor_base):
    q_hat = 2 ** (0.5/s_hat) * (n / m) ** (0.5/s_hat)
    k = ceil(log(n, 2))
    u = len(factor_base)/131987900 * (k ** -3.671828)
    for i in range(s_hat, 10000, 2):
        collisions_greater_than_iterations = calc_collision_prop(u, s_hat, i) > u
        if collisions_greater_than_iterations:
            break;







class rsa_quadratic_sieve_B_from_fixed:

    def __init__(self, n, m, factor_base, p_min_i, p_max_i):
        self.n = n
        self.m = m
        self.factor_base = factor_base
        self.p_min_i = p_min_i
        self.p_max_i = p_max_i
        self.a_history = set()
        s_hat = round(log(sqrt(2*n) / m) / log((MAX_PRIME_POLYNOMIAL - MIN_PRIME_POLYNOMIAL)/2))


    def build(self):
        q, a = find_a_and_q(self.n, self.m, self.factor_base, self.a_history, self.p_min_i, self.p_max_i)
        B = calculate_B_values(q, a, self.factor_base)
        g, h = find_polynomials_and_calculate_values(sum(B) % a, a, self.n, self.factor_base, True)
        return g, h, B
