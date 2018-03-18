import numpy as np


def build_poly(roots):
    if len(roots) == 0:
        return [1]
    else:
        roots.sort()
        p = np.array([[-r, 1] for r in roots], dtype=object)
        n = len(p)
        while n > 1:
            m, r = divmod(n, 2)
            tmp = [polymul(p[i], p[i+m]) for i in range(m)]
            if r:
                tmp[0] = polymul(tmp[0], p[-1])
            p = tmp
            n = m
        return p[0][::-1] * ((-1) ** len(roots))


def polymul(c1, c2):
    ret = np.convolve(c1, c2).tolist()
    return trimseq(ret)


def trimseq(seq):
    if len(seq) == 0:
        return seq
    else:
        for i in range(len(seq) - 1, -1, -1):
            if seq[i] != 0:
                break
        return seq[:i+1]


def polyval(p, x):
    y = 0
    for i in range(len(p)):
        y = y * x + p[i]
    return y
