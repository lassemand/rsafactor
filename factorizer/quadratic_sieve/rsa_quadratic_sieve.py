#!/usr/bin/python3 -O
import operator
import time
from math import sqrt, log2, ceil
import random

import math
from interface import implements

from factorizer.quadratic_sieve.factor_base_prime import factor_base_prime
from factorizer.quadratic_sieve.matrix_operations import build_matrices, build_index_matrix, solve_matrix_opt
from factorizer.quadratic_sieve.polynomial import polynomial
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import is_quadratic_residue, modular_square_root, inv_mod, lowest_set_bit, sqrt_int, \
    choose_nf_m
from helper.primes_sieve import primes_sieve

TRIAL_DIVISION_EPS = 20
MIN_PRIME_POLYNOMIAL = 400
MAX_PRIME_POLYNOMIAL = 4000
SMALLEST_PRIME_TO_BE_IN_SIEVE = 20
NUMBER_OF_RETRIES_FINDING_A = 20
TEST_COUNTER = 0


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
    q, a = find_best_a_and_q_values(n, m, factor_base)
    B = calculate_B_values(q, a, factor_base)
    g, h = find_polynomials_and_calculate_values(sum(B) % a, a, n, factor_base, True)
    return g, h, B


def find_next_poly(n, factor_base, i, g, B):
    v = lowest_set_bit(i) + 1
    z = -1 if ceil(i / (2 ** v)) & 1 else 1
    b = (g.b + 2 * z * B[v - 1]) % g.a
    return find_polynomials_and_calculate_values(b, g.a, n, factor_base, False)


def sieve_factor_base(factor_base, m):
    sieve_array = [0] * (2 * m + 1)
    for fb in factor_base:
        if fb.soln1 is None:
            continue
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
            break;
    return divisors_idx, a


def subtract_partial_relation_exponents(partial_relation_1, partial_relation_2):
    counter_1 = 0
    counter_2 = 0
    new_relation = []
    while counter_1 != len(partial_relation_1) or counter_2 != len(partial_relation_2):
        if (counter_2 != len(partial_relation_2)) and (counter_1 == len(partial_relation_1) or partial_relation_1[counter_1][0] > partial_relation_2[counter_2][0]):
            saved_result = (partial_relation_2[counter_2][0], -partial_relation_2[counter_2][1])
            counter_2 += 1
        elif (counter_1 != len(partial_relation_1)) and (counter_2 == len(partial_relation_2) or partial_relation_2[counter_2][0] > partial_relation_1[counter_1][0]):
            saved_result = (partial_relation_1[counter_1][0], partial_relation_1[counter_1][1])
            counter_1 += 1
        elif partial_relation_1[counter_1][0] == partial_relation_2[counter_2][0]:
            result = partial_relation_1[counter_1][1] - partial_relation_2[counter_2][1]
            saved_result = (partial_relation_1[counter_1][0], result)
            counter_1 += 1
            counter_2 += 1
            if result == 0:
                continue
        new_relation.append(saved_result)
    return new_relation


def partial_relation_to_full_relation(partial_relation, inverted_partial_relation, n):
    u = inverted_partial_relation[0] * partial_relation[0] % n
    v = (u ** 2) % n
    if u == 1 or v == 1:
        return None
    return u, v, subtract_partial_relation_exponents(partial_relation[1], inverted_partial_relation[1])


def trial_division(n, sieve_array, factor_base, smooth_relations, g, h, m,
                   req_relations, partial_relations, partial_relations_limit):
    global TEST_COUNTER
    limit = log2(m * sqrt(n)) - TRIAL_DIVISION_EPS
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            v = g.eval(x) % n
            divisors_idx, a = trial_divide(v, factor_base)
            if a == 1:
                u = h.eval(x)
                smooth_relations.append((u, v, divisors_idx))
            elif a < partial_relations_limit:
                if a not in partial_relations:
                    partial_relations[a] = (inv_mod((h.eval(x) % n), n), divisors_idx)
                else:
                    smooth_relation = partial_relation_to_full_relation((h.eval(x), divisors_idx), partial_relations[a], n)
                    if smooth_relation is not None:
                        TEST_COUNTER += 1
                        smooth_relations.append(smooth_relation)
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


def exponents_to_factor(exponents, factor_base, n):
    result = 1
    for (index, exponent) in enumerate(exponents):
        if exponent == 0:
            continue
        factor = factor_base[index].p
        if exponent < 0:
            factor = inv_mod(factor, n)
        result *= factor ** (abs(exponent) // 2)
    return result


def factor_from_square(n, square_indices, smooth_relations, factor_base):
    res = [1, 1]
    exponents = [0] * len(factor_base)
    for idx in square_indices:
        res[0] *= smooth_relations[idx][0]
        for factor in smooth_relations[idx][2]:
            exponents[factor[0]] += factor[1]
    res[1] = exponents_to_factor(exponents, factor_base, n)
    return math.gcd(res[0] + res[1], n)


def siqs_find_factors(n, perfect_squares, smooth_relations, factor_base):
    for square_indices in perfect_squares:
        fact = factor_from_square(n, square_indices, smooth_relations, factor_base)
        if fact != 1 and fact != n:
            return fact, int(n / fact)
    return None, None


def linear_algebra(smooth_relations, factor_base, n):
    binary_exponent_matrix = build_matrices(factor_base, smooth_relations)
    M_opt, M_n, M_m = build_index_matrix(binary_exponent_matrix)
    perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
    return siqs_find_factors(n, perfect_squares, smooth_relations, factor_base)


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


def find_smooth_relations(factor_base, required_congruence_ratio, smooth_relations, m, i_poly, n, partial_relation_limit):
    global p_min_i, p_max_i, TEST_COUNTER
    print("*** Step 1/2: Finding smooth relations ***")
    required_relations = round(len(factor_base) * required_congruence_ratio)
    enough_relations = False
    partial_relations = dict()
    p_min_i, p_max_i = calculate_limits(factor_base)
    TEST_COUNTER = 0
    while not enough_relations:
        if i_poly == 0:
            g, h, B = find_first_polynomial(n, m, factor_base)
        else:
            g, h = find_next_poly(n, factor_base, i_poly, g, B)
        i_poly += 1
        if i_poly >= 2 ** (len(B) - 1):
            i_poly = 0

        sieve_array = sieve_factor_base(factor_base, m)
        enough_relations = trial_division(
            n, sieve_array, factor_base, smooth_relations,
            g, h, m, required_relations, partial_relations, partial_relation_limit)
    print(TEST_COUNTER)


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
            find_smooth_relations(factor_base, required_congruence_ratio, smooth_relations,
                                  m, i_poly, self.n, factor_base[-1].p ** 2)
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05
            else:
                return p, q
