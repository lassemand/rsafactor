#!/usr/bin/python3 -O
import math
from math import log2

from interface import implements

from factorizer.quadratic_sieve.factor_base_prime import factor_base_prime
from factorizer.quadratic_sieve.matrix_operations import build_matrices, build_index_matrix, solve_matrix_opt
from factorizer.quadratic_sieve.rsa_quadratic_sieve_B_from_fixed import rsa_quadratic_sieve_B_from_fixed
from factorizer.quadratic_sieve.rsa_quadratic_sieve_B_from_variable import rsa_quadratic_sieve_B_from_variable
from factorizer.quadratic_sieve.rsa_quadratic_sieve_smooth_relations import rsa_quadratic_sieve_smooth_relations
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import is_quadratic_residue, modular_square_root, inv_mod, sqrt_int, \
    choose_nf_m
from helper.primes_sieve import primes_sieve


def factor_base_primes(n, nf, small_primes):
    factor_base = []
    for p in small_primes:
        if is_quadratic_residue(n, p):
            t = modular_square_root(n % p, p)
            lp = round(log2(p))
            factor_base.append(factor_base_prime(p, t, lp))
            if len(factor_base) >= nf:
                break
    return factor_base


def siqs_calc_sqrts(square_indices, smooth_relations):
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


class rsa_quadratic_sieve(implements(rsa_factorizer)):
    def __init__(self, n, e, polynomial_type):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.polynomial_type = polynomial_type

    def factorize(self):
        small_primes = primes_sieve(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)
        factor_base = factor_base_primes(self.n, nf, small_primes)
        success = False
        smooth_relations = []
        i_poly = 0
        if self.polynomial_type == 1:
            required_relations = round(len(factor_base) * 1.05)
            B_builder = rsa_quadratic_sieve_B_from_variable(self.n, m, factor_base)
        if self.polynomial_type == 2:
            required_relations = len(factor_base)+1
            B_builder = rsa_quadratic_sieve_B_from_fixed(self.n, m, factor_base)
        smooth_relations_finder = rsa_quadratic_sieve_smooth_relations(required_relations, B_builder)
        while not success:
            smooth_relations_finder.find(factor_base, smooth_relations, m, i_poly, self.n, factor_base[-1].p ** 2)
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                smooth_relations_finder.required_relations *= 1.02
            else:
                return p, q
