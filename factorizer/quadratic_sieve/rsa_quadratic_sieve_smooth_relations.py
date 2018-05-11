from math import ceil, log2, sqrt

from factorizer.quadratic_sieve.rsa_quadratic_sieve_helper import find_polynomials_and_calculate_values
from helper.cryptographic_methods import lowest_set_bit, inv_mod

SMALLEST_PRIME_TO_BE_IN_SIEVE = 20
TRIAL_DIVISION_EPS = 20


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


def trial_division(n, sieve_array, factor_base, smooth_relations, g, h, m,
                   req_relations, partial_relations, partial_relations_limit):
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
                        smooth_relations.append(smooth_relation)
            if len(smooth_relations) >= req_relations:
                return True
    return False


def find_next_poly(n, factor_base, i, g, B):
    v = lowest_set_bit(i) + 1
    z = -1 if ceil(i / (2 ** v)) & 1 else 1
    b = (g.b + 2 * z * B[v - 1]) % g.a
    return find_polynomials_and_calculate_values(b, g.a, n, factor_base, False)


class rsa_quadratic_sieve_smooth_relations:
    def __init__(self, required_relations, B_builder):
        self.required_relations = required_relations
        self.B_builder = B_builder

    def find(self, factor_base, smooth_relations, m, i_poly, n, partial_relation_limit):
        print("*** Step 1/2: Finding smooth relations ***")
        enough_relations = False
        partial_relations = dict()
        while not enough_relations:
            if i_poly == 0:
                g, h, B = self.B_builder.build()
            else:
                g, h = find_next_poly(n, factor_base, i_poly, g, B)
            i_poly += 1
            if i_poly >= 2 ** (len(B) - 1):
                i_poly = 0

            sieve_array = sieve_factor_base(factor_base, m)
            enough_relations = trial_division(
                n, sieve_array, factor_base, smooth_relations,
                g, h, m, self.required_relations, partial_relations, partial_relation_limit)
