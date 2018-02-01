import rsa

from factorizer.rsa_brute_force import rsa_brute_force


def generate_factorizer(bits, method):
    (pubkey, privkey) = rsa.newkeys(bits)
    return {
        'brute_force': rsa_brute_force(pubkey.n, pubkey.e),
    }[method]

def generate_factorizers_dict(bits_list, method):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item, method)
    return bits_dict
