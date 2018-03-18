import math
import random

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from multiprocessing import Queue, Process, Semaphore

from helper.polynomial_builder import build_poly, polyval


def compute_values(trial_n, n, k, a, i, semaphore):
    global xs, ys
    f = lambda u: (u ** (2 * k) + a) % n
    X = []
    Y = []
    x = random.randint(2, n - 1)
    y = x
    for _ in range(trial_n):
        x = f(x)
        y = f(f(y))
        X.append(x)
        Y.append(y)
    semaphore.acquire()
    xs[i].extend(X)
    ys[i].extend(Y)
    semaphore.release()

def correlation_product(xs, ys, queue, n):
    Q = 1
    for i in range(len(xs)):

        polynomial = build_poly(ys[i])
        for x in xs[i]:
            Q *= polyval(polynomial, x)
    queue.put(Q % n)



class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator



    def factorize(self, a=1):
        global xs, ys
        queue = Queue()
        # Step 1: Define prime K such that for some prime K p \equiv 1 \mod K'
        k = self.k_calculator.calculate(self.n)
        # Step 2: Define trial n, being a multiple of m, such that p = n^2m^2()gcd(p-1,"K)- have a good chance of being discovered
        trial_n = self.n_calculator.calculate(self.n, self.m, k)
        # Step 3. On each machine of m define an initial seed
        xs = [[] for _ in range(self.m)]
        ys = [[] for _ in range(self.m)]
        semaphore = Semaphore(1)
        process = [Process(target=compute_values, args=(trial_n, self.n, k, a, i, semaphore)) for i in range(self.m)]
        for t in process:
            t.start()

        for t in process:
            t.join()
        print("done building up sums")
        indexes = [((u * trial_n) // self.m, (((u + 1) * trial_n) // self.m) - 1) for u in range(self.m)]
        saved_args = [(xs[index[0]:index[1]], xs[index[0]:index[1]]) for index in indexes]
        process = [Process(target=correlation_product, args=(args[0], args[1], queue, self.n)) for args in saved_args]
        for t in process:
            t.start()
        for _ in process:
            Q = queue.get()
            p = math.gcd(Q, self.n)
            if p != 1:
                print("failed")
                return p, int(self.n / p)
        print("succeded")
        return self.factorize(a + 1)
