class factor_base_prime:
    """A factor base prime for the Self-Initializing Quadratic Sieve."""

    def __init__(self, p, tmem, lp):
        self.p = p
        self.soln1 = None
        self.soln2 = None
        self.tmem = tmem
        self.lp = lp
        self.ainv = None
