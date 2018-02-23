import rsa

from factorizer.dixon_random_squares.rsa_dixon_random_squares import rsa_dixon_random_squares
from factorizer.dixon_random_squares.rsa_dixon_random_squares_validate_congruence import \
    rsa_dixon_random_squares_test_congruence
from factorizer.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.rsa_brute_force import rsa_brute_force
from factorizer.rsa_pollard_rho import rsa_pollard_rho
from factorizer.rsa_pollard_rho_parallel_independent import rsa_pollard_rho_parallel_independent


def generate_factorizer(bits, method):
    (pubkey, privkey) = rsa.newkeys(bits)
    return {
        'brute_force': rsa_brute_force(pubkey.n, pubkey.e),
        'pollard_rho': rsa_pollard_rho(pubkey.n, pubkey.e),
        'brent_pollard_rho': rsa_brent_pollard_rho(pubkey.n, pubkey.e),
        'pollard_rho_parallel_independent': rsa_pollard_rho_parallel_independent(pubkey.n, pubkey.e),
        'dixon_random_square': rsa_dixon_random_squares(pubkey.n, pubkey.e, rsa_dixon_random_squares_test_congruence()),
    }[method]

def generate_factorizers_dict(bits_list, method):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item, method)
    return bits_dict
