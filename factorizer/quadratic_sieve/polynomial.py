class polynomial:
    """A polynomial used for the Self-Initializing Quadratic Sieve."""

    def __init__(self, coeff=[], a=None, b=None):
        self.coeff = coeff
        self.a = a
        self.b = b

    def eval(self, x):
        res = 0
        for a in reversed(self.coeff):
            res *= x
            res += a
        return res
