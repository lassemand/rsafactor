from multiprocessing import Queue
from multiprocessing import Process

from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer
from factorizer.rsa_pollard_rho import rsa_pollard_rho


def worker(n, e, q):
    fac = rsa_pollard_rho(n, e)
    q.put(fac.factorize())


class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def factorize(self, f = lambda u: u ** 2 + 1):
        q = Queue()
        process = [Process(target=worker, args=(self.n, self.e, q,)) for i in range(4)]
        for t in process:
            t.start()
        return q.get()
