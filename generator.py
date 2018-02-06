import rsa

from factorizer.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.rsa_brute_force import rsa_brute_force
from factorizer.rsa_pollard_rho import rsa_pollard_rho


def generate_factorizer(bits, method):
    (pubkey, privkey) = rsa.newkeys(bits)
    return {
        'brute_force': rsa_brute_force(pubkey.n, pubkey.e),
        'pollard_rho': rsa_pollard_rho(pubkey.n, pubkey.e),
        'brent_pollard_rho': rsa_brent_pollard_rho(pubkey.n, pubkey.e),
    }[method]

def generate_factorizers_dict(bits_list, method):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item, method)
    return bits_dict
