import math
import rsa
from interface import implements

from factorizer.dixon_random_squares.rsa_dixon_random_squares import rsa_dixon_random_squares
from factorizer.dixon_random_squares.rsa_dixon_random_squares_validate_congruence import \
    rsa_dixon_random_squares_test_congruence
from factorizer.pollard_rho.k_calculator import k_calculator
from factorizer.pollard_rho.n_calculator import n_calculator
from factorizer.pollard_rho.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.pollard_rho.rsa_pollard_rho import rsa_pollard_rho
from factorizer.pollard_rho.rsa_pollard_rho_parallel import rsa_pollard_rho_parallel
from factorizer.pollard_rho.rsa_pollard_rho_parallel_independent import rsa_pollard_rho_parallel_independent
from factorizer.rsa_brute_force import rsa_brute_force


def generate_factorizer(bits, method, processes):
    (pubkey, privkey) = rsa.newkeys(bits)
    return {
        'brute_force': rsa_brute_force(pubkey.n, pubkey.e),
        'pollard_rho': rsa_pollard_rho(pubkey.n, pubkey.e),
        'brent_pollard_rho': rsa_brent_pollard_rho(pubkey.n, pubkey.e),
        'pollard_rho_parallel': rsa_pollard_rho_parallel(pubkey.n, pubkey.e, processes, basic_k_calculator(), advanced_n_calculator()),
        'pollard_rho_parallel_independent': rsa_pollard_rho_parallel_independent(pubkey.n, pubkey.e),
        'dixon_random_square': rsa_dixon_random_squares(pubkey.n, pubkey.e, rsa_dixon_random_squares_test_congruence()),
    }[method]

def generate_factorizers_dict(bits_list, method, processes):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item, method, processes)
    return bits_dict


class basic_k_calculator(implements(k_calculator)):
    def calculate(self, n):
        return 20


class advanced_n_calculator(implements(n_calculator)):
    def calculate(self, n, m, k):
        return int(math.sqrt(n) / (math.sqrt(2) * m * 1000))
