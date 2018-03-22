import math
import uuid
import json

import pika
from interface import implements

from factorizer.quadratic_sieve.rsa_quadratic_sieve import linear_algebra, factor_base_primes
from factorizer.quadratic_sieve.rsa_quadratic_sieve_parallel_client import initiate_quadratic_sieve_parallel, \
    retrieve_smooth_relations
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import choose_nf_m
from helper.primes_sieve import seg_sieve_primes


class rsa_quadratic_sieve_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, server_ip):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.8 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.server_ip = server_ip

    def factorize(self):
        small_primes = seg_sieve_primes(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)
        factor_base = factor_base_primes(self.n, nf, small_primes)
        required_congruence_ratio = 1.05
        smooth_relations = []
        correlation_id = str(uuid.uuid1())
        while True:
            initiate_quadratic_sieve_parallel(self.server_ip, self.n, m, factor_base)
            retrieve_smooth_relations(self.server_ip)
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05
            else:
                return p, q
