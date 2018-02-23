import random
from multiprocessing import Queue
from multiprocessing import Process

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from factorizer.rsa_pollard_rho import rsa_pollard_rho


def worker(n, e, queue, i):
    fac = rsa_pollard_rho(n, e, i)
    a = random.randint(1, 101)
    queue.put(fac.factorize(f = lambda u: u ** 2 + a))


class rsa_pollard_rho_parallel_independent(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self, f = lambda u: u ** 2 + 1):
        queue = Queue()
        process = [Process(target=worker, args=(self.n, self.e, queue, i,)) for i in range(4)]
        for t in process:
            t.start()
        p, q = queue.get()
        for t in process:
            t.terminate()
        return p, q

