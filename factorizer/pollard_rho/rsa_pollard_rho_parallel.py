import math
import random
import numpy as np

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
import threading
from multiprocessing import Queue


def compute_values(queue, trial_n, n, k, a):
    f = lambda u: (u ** (2 * k) + a) % n
    Y = [None] * trial_n
    X = [None] * trial_n
    x = random.randint(2, n - 1)
    y = x
    for i in range(trial_n):
        x = f(x)
        y = f(f(y))
        X[i] = x
        Y[i] = y
    print("One thread done")
    queue.put((X, Y))


def correlation_product(xs, ys, queue):
    Q = 1
    for i in range(len(xs)):
        results = []
        for x in xs[i]:
            results.append(ys[i]-x)

        Q *= np.prod(np.polyval(ys[i], -xs[i]))
    queue.put(Q)

def eval(x, T, delta=4):
    d = len(x)
    if len(T) <= delta:
        return (x)




class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator



    def factorize(self, a=1):
        queue = Queue()
        # Step 1: Define prime K such that for some prime K p \equiv 1 \mod K'
        k = self.k_calculator.calculate(self.n)
        # Step 2: Define trial n, being a multiple of m, such that p = n^2m^2()gcd(p-1,"K)- have a good chance of being discovered
        trial_n = self.n_calculator.calculate(self.n, self.m, k)
        print("trial_n: " +  str(trial_n))
        # Step 3. On each machine of m define an initial seed
        process = [threading.Thread(target=compute_values, args=(queue, trial_n, self.n, k, a)) for _ in range(self.m)]
        for t in process:
            t.start()


        saved_ys = []
        saved_xs = []
        for _ in process:
            X, Y = queue.get()
            saved_ys.append(Y)
            saved_xs.append(X)
        print("Adding stuff to list done")
        saved_xs, saved_ys = np.array(saved_xs), np.array(saved_ys)
        indexes = [(int(u * trial_n / self.m), int((((u + 1) * trial_n) / self.m) - 1)) for u in range(self.m)]
        saved_args = [(saved_xs[index[0]:index[1]], saved_ys[index[0]:index[1]]) for index in indexes]
        process = [threading.Thread(target=correlation_product, args=(args[0], args[1], queue)) for args in saved_args]
        for t in process:
            t.start()
        for _ in process:
            print("Retrieved from one list")
            Q = queue.get()
            p = math.gcd(Q % self.n, self.n)
            if p != 1:
                print("Are we here")
                return p, int(self.n / p)
        print("Test")
        return self.factorize(a + 1)
