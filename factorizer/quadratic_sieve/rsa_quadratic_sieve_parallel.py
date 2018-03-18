import math

from interface import implements
from multiprocessing import Process, Queue

from factorizer.quadratic_sieve.rsa_quadratic_sieve import find_first_polynomial, siqs_find_next_poly, \
    sieve_factor_base, TRIAL_DIVISION_EPS, trial_divide, linear_algebra, factor_base_primes, find_smooth_relations
from factorizer.rsa_factorizer import rsa_factorizer
from helper.cryptographic_methods import choose_nf_m
from helper.primes_sieve import primes_sieve, seg_sieve_primes


def trial_division(n, sieve_array, factor_base, g, h, m, queue):
    limit = math.log2(m * math.sqrt(n)) - TRIAL_DIVISION_EPS
    smooth_relations = []
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            gx = g.eval(x)
            divisors_idx = trial_divide(gx, factor_base)
            if divisors_idx is not None:
                u = h.eval(x)
                v = gx
                smooth_relations.append((u, v, divisors_idx))
                if len(smooth_relations) > 50:
                    queue.put(smooth_relations)
                    smooth_relations = []
    queue.put(smooth_relations)


def find_smooth_relations(factor_base, m, i_poly, queue, n, g, h, B, processes):
    print("B: " + str(len(B)))
    while i_poly < 2 ** (len(B) - 1):
        g, h = siqs_find_next_poly(n, factor_base, i_poly, g, B)
        i_poly += (i_poly * processes)
        sieve_array = sieve_factor_base(factor_base, m)
        trial_division(n, sieve_array, factor_base, g, h, m, queue)
    queue.put(False)


class rsa_quadratic_sieve_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m):
        self.n = n
        self.e = e
        self.y = int(math.exp(0.8 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.m = m

    def factorize(self):
        queue = Queue()
        small_primes = seg_sieve_primes(self.y)
        dig = len(str(self.n))
        nf, m = choose_nf_m(dig)
        factor_base = factor_base_primes(self.n, nf, small_primes)
        required_congruence_ratio = 1.05
        smooth_relations = []
        while True:
            while len(smooth_relations) < round(len(factor_base) * required_congruence_ratio):
                print("Start")
                g, h, B = find_first_polynomial(self.n, m, factor_base)
                process = [Process(target=find_smooth_relations, args=(factor_base, m, i + 1, queue, self.n, g, h, B, self.m)) for i
                           in
                           range(self.m)]
                for t in process:
                    t.start()
                finished_thread_counter = 0
                while finished_thread_counter < self.m:
                    content = queue.get()
                    if isinstance(content, list) and finished_thread_counter == 0:
                        smooth_relations.extend(content)
                    else:
                        print("Done here")
                        finished_thread_counter += 1

                for t in process:
                    if t.is_alive():
                        t.terminate()
            print("Done handling stuff")
            p, q = linear_algebra(smooth_relations, factor_base, self.n)
            if p is None or q is None:
                print("Failed to find a solution. Finding more relations...")
                required_congruence_ratio += 0.05
            else:
                return p, q
