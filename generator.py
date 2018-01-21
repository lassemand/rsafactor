import rsa

from factorizer.rsa_brute_force import rsa_brute_force


def generate_factorizer(bits):
    (pubkey, privkey) = rsa.newkeys(bits)
    return rsa_brute_force(pubkey.n, pubkey.e)

def generate_factorizers_dict(bits_list):
    bits_dict = {}
    for (index, item) in enumerate(bits_list):
        bits_dict[item] = generate_factorizer(item)
    return bits_dict
