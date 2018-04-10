#!/usr/bin/python3 -O
import time
from math import sqrt, log2, ceil
import random

import math
from interface import implements

from factorizer.quadratic_sieve.factor_base_prime import factor_base_prime
from factorizer.quadratic_sieve.matrix_operations import build_binary_matrix, build_index_matrix, solve_matrix_opt
from factorizer.quadratic_sieve.polynomial import polynomial
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import is_quadratic_residue, modular_square_root, inv_mod, lowest_set_bit, \
    is_probable_prime, sqrt_int, choose_nf_m
from helper.primes_sieve import primes_sieve

TRIAL_DIVISION_EPS = 20
MIN_PRIME_POLYNOMIAL = 400
MAX_PRIME_POLYNOMIAL = 4000
SMALLEST_PRIME_TO_BE_IN_SIEVE = 20
NUMBER_OF_RETRIES_FINDING_A = 20


def factor_base_primes(n, nf, small_primes):
    """Compute and return nf factor base primes suitable for a Quadratic
    Sieve on the number n.
    """
    factor_base = []
    for p in small_primes:
        if is_quadratic_residue(n, p):
            t = modular_square_root(n % p, p)
            lp = round(log2(p))
            factor_base.append(factor_base_prime(p, t, lp))
            if len(factor_base) >= nf:
                break
    return factor_base


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


def calculate_limits(factor_base):
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


def find_best_a_and_q_values(n, m, factor_base):
    global p_min_i, p_max_i
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


def find_first_polynomial(n, m, factor_base):
    """Compute the first of a set of polynomials for the Self-
    Initialising Quadratic Sieve.
    """
    q, a = find_best_a_and_q_values(n, m, factor_base)
    B = calculate_B_values(q, a, factor_base)
    g, h = find_polynomials_and_calculate_values(sum(B) % a, a, n, factor_base, True)
    return g, h, B


def find_next_poly(n, factor_base, i, g, B):
    """Compute the (i+1)-th polynomials for the Self-Initialising
    Quadratic Sieve, given that g is the i-th polynomial.
    """
    v = lowest_set_bit(i) + 1
    z = -1 if ceil(i / (2 ** v)) & 1 else 1
    b = (g.b + 2 * z * B[v - 1]) % g.a
    a = g.a
    return find_polynomials_and_calculate_values(b, a, n, factor_base, False)


def sieve_factor_base(factor_base, m):
    """Perform the sieving step of the SIQS. Return the sieve array."""
    sieve_array = [0] * (2 * m + 1)
    for fb in factor_base:
        if fb.soln1 is None:
            continue
        # TODO: Make this value dynamic
        if fb.p > SMALLEST_PRIME_TO_BE_IN_SIEVE:
            i_start_1 = ((m + fb.soln1) // fb.p)
            a_start_1 = fb.soln1 - i_start_1 * fb.p
            for a in range(a_start_1 + m, 2 * m + 1, fb.p):
                sieve_array[a] += fb.lp

            i_start_2 = -((m + fb.soln2) // fb.p)
            a_start_2 = fb.soln2 + i_start_2 * fb.p
            for a in range(a_start_2 + m, 2 * m + 1, fb.p):
                sieve_array[a] += fb.lp
    return sieve_array


def trial_divide(a, factor_base):
    """Determine whether the given number a can be fully factorised into
    primes from the factors base. If so, return the indices of the
    factors from the factor base. If not, return None.
    """
    divisors_idx = []
    for i, fb in enumerate(factor_base):
        if a % fb.p == 0:
            exp = 1
            a //= fb.p
            while a % fb.p == 0:
                a //= fb.p
                exp += 1
            divisors_idx.append((i, exp))
        if a == 1:
            return divisors_idx
    return None


def trial_division(n, sieve_array, factor_base, smooth_relations, g, h, m,
                   req_relations):
    limit = log2(m * sqrt(n)) - TRIAL_DIVISION_EPS
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            gx = g.eval(x)
            divisors_idx = trial_divide(gx, factor_base)
            if divisors_idx is not None:
                u = h.eval(x)
                v = gx
                smooth_relations.append((u, v, divisors_idx))
                if len(smooth_relations) >= req_relations:
                    return True
    return False


def siqs_calc_sqrts(square_indices, smooth_relations):
    """Given on of the solutions returned by siqs_solve_matrix_opt and
    the corresponding smooth relations, calculate the pair [a, b], such
    that a^2 = b^2 (mod n).
    """
    res = [1, 1]
    for idx in square_indices:
        res[0] *= smooth_relations[idx][0]
        res[1] *= smooth_relations[idx][1]
    res[1] = sqrt_int(res[1])
    return res


def factor_from_square(n, square_indices, smooth_relations):
    """Given one of the solutions returned by siqs_solve_matrix_opt,
    return the factor f determined by f = gcd(a - b, n), where
    a, b are calculated from the solution such that a*a = b*b (mod n).
    Return f, a factor of n (possibly a trivial one).
    """
    sqrt1, sqrt2 = siqs_calc_sqrts(square_indices, smooth_relations)
    return math.gcd(abs(sqrt1 - sqrt2), n)


def siqs_find_factors(n, perfect_squares, smooth_relations):
    """Perform the last step of the Self-Initialising Quadratic Field.
    Given the solutions returned by siqs_solve_matrix_opt, attempt to
    identify a number of (not necessarily prime) factors of n, and
    return them.
    """
    for square_indices in perfect_squares:
        fact = factor_from_square(n, square_indices, smooth_relations)
        if fact != 1:
            return fact, int(n / fact)
    return None, None


def linear_algebra(smooth_relations, factor_base, n):
    M = build_binary_matrix(factor_base, smooth_relations)
    M_opt, M_n, M_m = build_index_matrix(M)
    perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
    return siqs_find_factors(n, perfect_squares, smooth_relations)


def siqs_find_more_factors_gcd(numbers):
    res = set()
    for n in numbers:
        res.add(n)
        for m in numbers:
            if n != m:
                fact = math.gcd(n, m)
                if fact != 1 and fact != n and fact != m:
                    if fact not in res:
                        print("SIQS: GCD found non-trivial factor: %d" % fact)
                        res.add(fact)
                    res.add(n // fact)
                    res.add(m // fact)
    return res


def find_smooth_relations(factor_base, required_congruence_ratio, smooth_relations, m, i_poly, n):
    global p_min_i, p_max_i
    print("*** Step 1/2: Finding smooth relations ***")
    required_relations = round(len(factor_base) * required_congruence_ratio)
    enough_relations = False
    p_min_i, p_max_i = calculate_limits(factor_base)
    found_relations_counter = 0
    while not enough_relations:
        if i_poly == 0:
            found_relations_counter += 1
            g, h, B = find_first_polynomial(n, m, factor_base)
        else:
            g, h = find_next_poly(n, factor_base, i_poly, g, B)
        i_poly += 1
        if i_poly >= 2 ** (len(B) - 1):
            i_poly = 0

        sieve_array = sieve_factor_base(factor_base, m)
        enough_relations = trial_division(
            n, sieve_array, factor_base, smooth_relations,
            g, h, m, required_relations)


class rsa_quadratic_sieve(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))

    def factorize(self):
        small_primes = primes_sieve(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)
        factor_base = factor_base_primes(self.n, nf, small_primes)
        required_congruence_ratio = 1.05
        success = False
        smooth_relations = []
        i_poly = 0
        while not success:
            start_time = int(round(time.time() * 1000))
            find_smooth_relations(factor_base, required_congruence_ratio, smooth_relations, m, i_poly, self.n)
            end_time = int(round(time.time() * 1000))
            print("Smooth_relations: " + str(end_time - start_time))
            start_time = int(round(time.time() * 1000))
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            end_time = int(round(time.time() * 1000))
            print("Linear Algebra: " + str(end_time - start_time))
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05
            else:
                return p, q
