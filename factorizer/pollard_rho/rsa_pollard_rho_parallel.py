import math
import random

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from multiprocessing import Process
from multiprocessing import Queue


class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator

    def pollard_rho_worker(self, trial_n, k, i, queue, f):
        x = random.randint(2, self.n - 1)
        y = x
        Q = 1
        for i in range(1, trial_n):
            x = f(x)
            y = f(f(y))

        return 1, 1


    def factorize(self, a = 1):
        queue = Queue()
        # Step 1: Define prime K such that for some prime K p \equiv 1 \mod K'
        k = self.k_calculator.calculate(self.n)
        # Step 2: Define trial n, being a multiple of m, such that p = n^2m^2()gcd(p-1,"K)- have a good chance of being discovered
        trial_n = self.n_calculator(self.n, self.m, k)
        # Step 3. On each machine of m define an initial seed
        process = [Process(target=self.pollard_rho_worker, args=(trial_n, k, i, queue)) for i in range(self.m)]
        for t in process:
            t.start()
        # Step 4:
        return p, int(self.n / p)
