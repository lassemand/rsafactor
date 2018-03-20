import math
import rsa
from interface import implements

from factorizer.dixon_random_squares.rsa_dixon_random_squares import rsa_dixon_random_squares
from factorizer.dixon_random_squares.rsa_dixon_random_squares_parallel import rsa_dixon_random_squares_parallel
from factorizer.dixon_random_squares.rsa_dixon_random_squares_validate_congruence import \
    rsa_dixon_random_squares_test_congruence
from factorizer.pollard_rho.k_calculator import k_calculator
from factorizer.pollard_rho.n_calculator import n_calculator
from factorizer.pollard_rho.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.pollard_rho.rsa_pollard_rho import rsa_pollard_rho
from factorizer.pollard_rho.rsa_pollard_rho_parallel import rsa_pollard_rho_parallel, advanced_n_calculator
from factorizer.pollard_rho.rsa_pollard_rho_parallel_independent import rsa_pollard_rho_parallel_independent
from factorizer.quadratic_sieve.rsa_quadratic_sieve import rsa_quadratic_sieve
from factorizer.quadratic_sieve.rsa_quadratic_sieve_parallel import rsa_quadratic_sieve_parallel
from factorizer.rsa_brute_force import rsa_brute_force


def generate_factorizer(bits, method, processes, worker_ips, server_ip):
    (pubkey, privkey) = rsa.newkeys(bits)
    return {
        'brute_force': rsa_brute_force(pubkey.n, pubkey.e),
        'pollard_rho': rsa_pollard_rho(pubkey.n, pubkey.e),
        'brent_pollard_rho': rsa_brent_pollard_rho(pubkey.n, pubkey.e),
        'pollard_rho_parallel': rsa_pollard_rho_parallel(pubkey.n, pubkey.e, processes, basic_k_calculator(), advanced_n_calculator(bits), worker_ips, server_ip),
        'pollard_rho_parallel_independent': rsa_pollard_rho_parallel_independent(pubkey.n, pubkey.e),
        'dixon_random_square': rsa_dixon_random_squares(pubkey.n, pubkey.e, rsa_dixon_random_squares_test_congruence()),
        'dixon_random_square_parallel': rsa_dixon_random_squares_parallel(pubkey.n, pubkey.e, processes, rsa_dixon_random_squares_test_congruence()),
        'quadratic_sieve': rsa_quadratic_sieve(pubkey.n, pubkey.e),
        'quadratic_sieve_parallel': rsa_quadratic_sieve_parallel(pubkey.n, pubkey.e, processes),
    }[method]


def generate_factorizers_dict(bits_list, method, processes, worker_ips, server_ip):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item, method, processes, worker_ips, server_ip)
    return bits_dict


class basic_k_calculator(implements(k_calculator)):
    def calculate(self, n):
        return 1


