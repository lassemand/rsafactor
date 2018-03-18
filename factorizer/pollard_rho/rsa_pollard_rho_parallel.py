import math
import random

from interface import implements

from factorizer.pollard_rho.rsa_pollard_rho_parallel_client import initiate_pollard_rho_parallel
from factorizer.rsa_factorizer import rsa_factorizer
from multiprocessing import Queue, Process, Semaphore








class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator, worker_ips, server_ip):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator
        self.worker_ips = worker_ips
        self.server_ip = server_ip



    def factorize(self, a=1):
        global xs, ys
        queue = Queue()
        # Step 1: Define prime K such that for some prime K p \equiv 1 \mod K'
        k = self.k_calculator.calculate(self.n)
        # Step 2: Define trial n, being a multiple of m, such that p = n^2m^2()gcd(p-1,"K)- have a good chance of being discovered
        trial_n = self.n_calculator.calculate(self.n, self.m, k)
        # Step 3. On each machine of m define an initial seed
        initiate_pollard_rho_parallel(trial_n, self.n, k, a, self.worker_ips, self.server_ip)
        p, q = create_pollard_rho_parallel_return_queue

