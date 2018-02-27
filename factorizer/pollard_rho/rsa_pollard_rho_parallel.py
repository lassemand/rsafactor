import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from multiprocessing import Process
from multiprocessing import Queue


def compute_values(queue, trial_n, n, k, a):
    f = lambda u: u ** (2 * k) + a % n
    Y = [None] * trial_n
    X = [None] * trial_n
    x = random.randint(2, n - 1)
    y = x
    for i in range(trial_n):
        x = f(x)
        y = f(f(y))
        X[i] = x
        Y[i] = y
    queue.put((X, Y))

def pollard_rho_parallel(xs, ys, queue):
    Q = 1
    for i in range(len(xs)):
        X = xs[i]
        Y = ys[i]
        for y in Y:
            for x in X:
                Q *= y - x
    queue.put(Q)


class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator


    def factorize(self, a=1):
        done_threads_counter = 0
        queue = Queue()
        # Step 1: Define prime K such that for some prime K p \equiv 1 \mod K'
        k = self.k_calculator.calculate(self.n)
        # Step 2: Define trial n, being a multiple of m, such that p = n^2m^2()gcd(p-1,"K)- have a good chance of being discovered
        trial_n = self.n_calculator.calculate(self.n, self.m, k)
        # Step 3. On each machine of m define an initial seed
        process = [Process(target=compute_values, args=(queue, trial_n, self.n, k, a)) for _ in range(self.m)]
        for t in process:
            t.start()

        saved_ys = []
        saved_xs = []
        print("first")
        for _ in process:
            X, Y = queue.get()
            saved_ys.append(Y)
            saved_xs.append(X)
        saved_xs, saved_ys = np.array(saved_xs), np.array(saved_ys)
        indexes = [(int(u * trial_n / self.m), int((((u + 1) * trial_n) / self.m) - 1)) for u in range(self.m)]
        saved_args = [(saved_xs[index[0]:index[1]], saved_ys[index[0]:index[1]]) for index in indexes]
        print("second")
        process = [Process(target=pollard_rho_parallel, args=(args[0], args[1], queue)) for args in saved_args]
        for t in process:
            t.start()
        print("third")
        # TODO make a count
        for _ in process:
            Q = queue.get()
            p = math.gcd(Q % self.n, self.n)
            if p != 1:
                return p, int(self.n / p)
        return self.factorize(a + 1)
