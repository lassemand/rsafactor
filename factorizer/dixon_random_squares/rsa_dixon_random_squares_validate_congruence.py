import math
from interface import implements
import numpy as np

from factorizer.dixon_random_squares.dixon_congruence_validator import dixon_congruence_validator


class rsa_dixon_random_squares_test_congruence(implements(dixon_congruence_validator)):

    def validate(self, forced_ones, Z, all_rows_in_factor, B, n):
        list_z_values = list(forced_ones)
        z_congruence = np.prod(Z[list_z_values]) % n
        exponent_sum = np.sum(all_rows_in_factor[list_z_values, :], axis=0, dtype=int)
        y_congruence = 1
        for index in range(len(B)):
            y_congruence = (y_congruence * B[index] ** (exponent_sum[index].item() // 2)) % n
        p = math.gcd(z_congruence + y_congruence, n)
        if p != 1 and p != n:
            return p, int(n / p)
        return None, None

