#!/usr/bin/python3 -O

from math import sqrt, log2, ceil
import random

import math
from interface import implements

from factorizer.quadratic_sieve.factor_base_prime import factor_base_prime
from factorizer.quadratic_sieve.matrix_operations import siqs_build_matrix, siqs_build_matrix_opt, siqs_solve_matrix_opt
from factorizer.quadratic_sieve.polynomial import polynomial
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import is_quadratic_residue, modular_square_root, inv_mod, lowest_set_bit, \
    is_probable_prime, sqrt_int, choose_nf_m
from helper.primes_sieve import primes_sieve

SIQS_TRIAL_DIVISION_EPS = 25
SIQS_MIN_PRIME_POLYNOMIAL = 400
SIQS_MAX_PRIME_POLYNOMIAL = 4000


def factor_base_primes(n, nf):
    """Compute and return nf factor base primes suitable for a Quadratic
    Sieve on the number n.
    """
    global small_primes
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
        if p_min_i is None and fb.p >= SIQS_MIN_PRIME_POLYNOMIAL:
            p_min_i = i
        if p_max_i is None and fb.p > SIQS_MAX_PRIME_POLYNOMIAL:
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


def find_best_a_and_q_values(n, m, p_min_i, p_max_i, factor_base):
    target = sqrt(2 * float(n)) / m
    target1 = target / ((factor_base[p_min_i].p +
                         factor_base[p_max_i].p) / 2) ** 0.5
    best_q, best_a, best_ratio = None, None, None
    for _ in range(30):
        a = 1
        q = []

        while a < target1:
            p_i = 0
            while p_i == 0 or p_i in q:
                p_i = random.randint(p_min_i, p_max_i)
            p = factor_base[p_i].p
            a *= p
            q.append(p_i)

        ratio = a / target

        if (best_ratio is None or (0.9 <= ratio < best_ratio) or
                        best_ratio < 0.9 and ratio > best_ratio):
            best_q = q
            best_a = a
            best_ratio = ratio
    return best_q, best_a


def find_first_polynomial(n, m, factor_base):
    """Compute the first of a set of polynomials for the Self-
    Initialising Quadratic Sieve.
    """
    p_min_i, p_max_i = calculate_limits(factor_base)
    q, a = find_best_a_and_q_values(n, m, p_min_i, p_max_i, factor_base)
    B = calculate_B_values(q, a, factor_base)
    g, h = find_polynomials_and_calculate_values(sum(B) % a, a, n, factor_base, True)
    return g, h, B


def siqs_find_next_poly(n, factor_base, i, g, B):
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
        if fb.p > 20:
            i_start_1 = ((m + fb.soln1) // fb.p)
            a_start_1 = fb.soln1 - i_start_1 * fb.p
            for a in range(a_start_1 + m, 2 * m + 1, fb.p):
                sieve_array[a] += fb.lp

            i_start_2 = -((m + fb.soln2) // fb.p)
            a_start_2 = fb.soln2 + i_start_2 * fb.p
            for a in range(a_start_2 + m, 2 * m + 1, fb.p):
                sieve_array[a] += fb.lp
    return sieve_array


def siqs_trial_divide(a, factor_base):
    """Determine whether the given number a can be fully factorised into
    primes from the factors base. If so, return the indices of the
    factors from the factor base. If not, return None.
    """
    divisors_idx = []
    for i, fb in enumerate(factor_base):
        if a % fb.p == 0:
            exp = 0
            while a % fb.p == 0:
                a //= fb.p
                exp += 1
            divisors_idx.append((i, exp))
        if a == 1:
            return divisors_idx
    return None


def siqs_trial_division(n, sieve_array, factor_base, smooth_relations, g, h, m,
                        req_relations):
    """Perform the trial division step of the Self-Initializing
    Quadratic Sieve.
    """
    sqrt_n = sqrt(float(n))
    limit = log2(m * sqrt_n) - SIQS_TRIAL_DIVISION_EPS
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            gx = g.eval(x)
            divisors_idx = siqs_trial_divide(gx, factor_base)
            if divisors_idx is not None:
                u = h.eval(x)
                v = gx
                assert (u * u) % n == v % n
                smooth_relations.append((u, v, divisors_idx))
                if (len(smooth_relations) >= req_relations):
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


def siqs_factor_from_square(n, square_indices, smooth_relations):
    """Given one of the solutions returned by siqs_solve_matrix_opt,
    return the factor f determined by f = gcd(a - b, n), where
    a, b are calculated from the solution such that a*a = b*b (mod n).
    Return f, a factor of n (possibly a trivial one).
    """
    sqrt1, sqrt2 = siqs_calc_sqrts(square_indices, smooth_relations)
    assert (sqrt1 * sqrt1) % n == (sqrt2 * sqrt2) % n
    return math.gcd(abs(sqrt1 - sqrt2), n)


def siqs_find_factors(n, perfect_squares, smooth_relations):
    """Perform the last step of the Self-Initialising Quadratic Field.
    Given the solutions returned by siqs_solve_matrix_opt, attempt to
    identify a number of (not necessarily prime) factors of n, and
    return them.
    """
    factors = []
    rem = n
    non_prime_factors = set()
    prime_factors = set()
    for square_indices in perfect_squares:
        fact = siqs_factor_from_square(n, square_indices, smooth_relations)
        if fact != 1 and fact != rem:
            if is_probable_prime(fact):
                if fact not in prime_factors:
                    print("SIQS: Prime factor found: %d" % fact)
                    prime_factors.add(fact)

                while rem % fact == 0:
                    factors.append(fact)
                    rem //= fact

                if rem == 1:
                    break
                if is_probable_prime(rem):
                    factors.append(rem)
                    rem = 1
                    break
            else:
                if fact not in non_prime_factors:
                    print("SIQS: Non-prime factor found: %d" % fact)
                    non_prime_factors.add(fact)

    if rem != 1 and non_prime_factors:
        non_prime_factors.add(rem)
        for fact in sorted(siqs_find_more_factors_gcd(non_prime_factors)):
            while fact != 1 and rem % fact == 0:
                print("SIQS: Prime factor found: %d" % fact)
                factors.append(fact)
                rem //= fact
            if rem == 1 or is_probable_prime(rem):
                break

    if rem != 1:
        factors.append(rem)
    return factors


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


class rsa_quadratic_sieve(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))

    def factorize(self):
        global small_primes
        """Factorise the given integer n >= 1 into its prime factors."""
        small_primes = primes_sieve(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)

        factor_base = factor_base_primes(self.n, nf)

        required_congruence_ratio = 1.05
        success = False
        smooth_relations = []
        prev_cnt = 0
        i_poly = 0
        while not success:
            print("*** Step 1/2: Finding smooth relations ***")
            required_relations = round(len(factor_base) * required_congruence_ratio)
            print("Target: %d relations" % required_relations)
            enough_relations = False
            while not enough_relations:
                if i_poly == 0:
                    g, h, B = find_first_polynomial(self.n, m, factor_base)
                else:
                    g, h = siqs_find_next_poly(self.n, factor_base, i_poly, g, B)
                i_poly += 1
                if i_poly >= 2 ** (len(B) - 1):
                    i_poly = 0
                sieve_array = sieve_factor_base(factor_base, m)
                enough_relations = siqs_trial_division(
                    self.n, sieve_array, factor_base, smooth_relations,
                    g, h, m, required_relations)

                if (len(smooth_relations) >= required_relations or
                                    i_poly % 8 == 0 and len(smooth_relations) > prev_cnt):
                    print("Total %d/%d relations." %
                          (len(smooth_relations), required_relations))
                    prev_cnt = len(smooth_relations)

            print("*** Step 2/2: Linear Algebra ***")
            print("Building matrix for linear algebra step...")
            M = siqs_build_matrix(factor_base, smooth_relations)
            M_opt, M_n, M_m = siqs_build_matrix_opt(M)

            print("Finding perfect squares using matrix...")
            perfect_squares = siqs_solve_matrix_opt(M_opt, M_n, M_m)

            print("Finding factors from perfect squares...")
            factors = siqs_find_factors(self.n, perfect_squares, smooth_relations)
            if len(factors) == 1:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05

            return factors[0], int(self.n / factors[0])
