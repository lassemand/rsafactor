import math
from interface import implements

from factorizer.quadratic_sieve.rsa_quadratic_sieve import linear_algebra
from factorizer.quadratic_sieve.rsa_quadratic_sieve_parallel_client import initiate_quadratic_sieve_parallel, \
    retrieve_smooth_relations
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import choose_nf_m, is_quadratic_residue, modular_square_root
from helper.primes_sieve import primes_sieve


def factor_base_primes(n, nf, small_primes):
    """Compute and return nf factor base primes suitable for a Quadratic
    Sieve on the number n.
    """
    factor_base = []
    for p in small_primes:
        if is_quadratic_residue(n, p):
            t = modular_square_root(n % p, p)
            lp = round(math.log2(p))
            factor_base.append((p, t, lp))
            if len(factor_base) >= nf:
                break
    return factor_base


class rsa_quadratic_sieve_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, server_ip):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.server_ip = server_ip

    def factorize(self):
        small_primes = primes_sieve(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)
        factor_base = factor_base_primes(self.n, nf, small_primes)
        required_congruence_ratio = 1.05
        while True:
            initiate_quadratic_sieve_parallel(self.server_ip, self.n, m, factor_base)
            smooth_relations = retrieve_smooth_relations(self.server_ip,
                                                         round(len(factor_base) * required_congruence_ratio))
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05
            else:
                return p, q
