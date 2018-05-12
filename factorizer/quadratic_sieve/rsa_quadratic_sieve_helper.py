from factorizer.quadratic_sieve.polynomial import polynomial
from helper.cryptographic_methods import inv_mod
MIN_PRIME_POLYNOMIAL = 400
MAX_PRIME_POLYNOMIAL = 4000


def calculate_limits_variable(factor_base):
    p_min_i = None
    p_max_i = None
    for i, fb in enumerate(factor_base):
        if p_min_i is None and fb.p >= MIN_PRIME_POLYNOMIAL:
            p_min_i = i
        if p_max_i is None and fb.p > MAX_PRIME_POLYNOMIAL:
            p_max_i = i - 1
            break

    # The following may happen if the factor base is small, make sure
    # that we have enough primes.
    if p_max_i is None:
        p_max_i = len(factor_base) - 1
    if p_min_i is None or p_max_i - p_min_i < 20:
        p_min_i = min(p_min_i, 5)
    return p_min_i, p_max_i


def calculate_B_values(q, a, factor_base):
    B = []
    for q_i in q:
        fb_l = factor_base[q_i]
        q_l = fb_l.p
        gamma = (fb_l.tmem * inv_mod(a // q_l, q_l)) % q_l
        if gamma > q_l // 2:
            gamma = q_l - gamma
        B.append(a // q_l * gamma)
    return B


def find_polynomials_and_calculate_values(b, a, n, factor_base, is_first_time):
    b_orig = b
    if 2 * b > a:
        b = a - b

    g = polynomial([b * b - n, 2 * a * b, a * a], a, b_orig)
    h = polynomial([b, a])
    for fb in factor_base:
        if a % fb.p != 0:
            if is_first_time:
                fb.ainv = inv_mod(a, fb.p)
            fb.soln1 = (fb.ainv * (fb.tmem - b)) % fb.p
            fb.soln2 = (fb.ainv * (-fb.tmem - b)) % fb.p
    return g, h
