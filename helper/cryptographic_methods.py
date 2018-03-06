# Number of iterations for the Miller-Rabin primality test
import random
from math import floor, log2

MILLER_RABIN_ITERATIONS = 50

def lowest_set_bit(a):
    b = (a & -a)
    low_bit = -1
    while b:
        b >>= 1
        low_bit += 1
    return low_bit


def to_bits(k):
    """Return a generator that returns the bits of k, starting from the
    least significant bit, using True for 1s, and False for 0s.
    """
    k_binary = bin(k)[2:]
    return (bit == '1' for bit in k_binary[::-1])


def pow_mod(a, k, m):
    """Return a^k mod m."""
    r = 1
    b = a
    for bit in to_bits(k):
        if bit:
            r = (r * b) % m
        b = (b * b) % m
    return r


def is_quadratic_residue(a, p):
    """Return whether a is a quadratic residue modulo a prime p."""
    return legendre(a, (p - 1) // 2, 1, p) == 1


def legendre(a, q, l, n):
    x = q ** l
    if x == 0:
        return 1

    z = 1
    a %= n

    while x != 0:
        if x % 2 == 0:
            a = (a ** 2) % n
            x //= 2
        else:
            x -= 1
            z = (z * a) % n
    return z


def sqrt_mod_prime(a, p):
    """Return the square root of a modulo the prime p. Behaviour is
    undefined if a is not a quadratic residue mod p."""
    # Algorithm from http://www.mersennewiki.org/index.php/Modular_Square_Root
    assert a < p
    assert is_probable_prime(p)
    if a == 0:
        return 0
    if p == 2:
        return a
    if p % 2 == 0:
        return None
    p_mod_8 = p % 8
    if p_mod_8 == 1:
        # Shanks method
        q = p // 8
        e = 3
        while q % 2 == 0:
            q //= 2
            e += 1
        while True:
            x = random.randint(2, p - 1)
            z = pow_mod(x, q, p)
            if pow_mod(z, 2 ** (e - 1), p) != 1:
                break
        y = z
        r = e
        x = pow_mod(a, (q - 1) // 2, p)
        v = (a * x) % p
        w = (v * x) % p
        while True:
            if w == 1:
                return v
            k = 1
            while pow_mod(w, 2 ** k, p) != 1:
                k += 1
            d = pow_mod(y, 2 ** (r - k - 1), p)
            y = (d ** 2) % p
            r = k
            v = (d * v) % p
            w = (w * y) % p
    elif p_mod_8 == 5:
        v = pow_mod(2 * a, (p - 5) // 8, p)
        i = (2 * a * v * v) % p
        return (a * v * (i - 1)) % p
    else:
        return pow_mod(a, (p + 1) // 4, p)


def inv_mod(a, m):
    """Return the modular inverse of a mod m."""
    return eea(a, m)[0] % m


def eea(a, b):
    """Solve the equation a*x + b*y = gcd(a,b).
    Return (x, y, +/-gcd(a,b)).
    """
    if a == 0:
        return (0, 1, b)
    x = eea(b % a, a)
    return (x[1] - b // a * x[0], x[0], x[2])


def is_probable_prime(a):
    """Perform the Miller-Rabin primality test to determine whether the
    given number a is a prime. Return True if the number is a prime
    with very high probability, and False if it is definitely composite.
    """
    if a == 2:
        return True
    if a == 1 or a % 2 == 0:
        return False
    return primality_test_miller_rabin(a, MILLER_RABIN_ITERATIONS)


def primality_test_miller_rabin(a, iterations):
    m = a - 1
    lb = lowest_set_bit(m)
    m >>= lb

    for _ in range(iterations):
        b = random.randint(2, a - 1)
        j = 0
        z = pow_mod(b, m, a)
        while not ((j == 0 and z == 1) or z == a - 1):
            if (j > 0 and z == 1 or j + 1 == lb):
                return False
            j += 1
            z = (z * z) % a

    return True


def sqrt_int(n):
    """Return the square root of the given integer, rounded down to the
    nearest integer.
    """
    a = n
    s = 0
    o = 1 << (floor(log2(n)) & ~1)
    while o != 0:
        t = s + o
        if a >= t:
            a -= t
            s = (s >> 1) + o
        else:
            s >>= 1
        o >>= 2
    return s


def kth_root_int(n, k):
    """Return the k-th root of the given integer n, rounded down to the
    nearest integer.
    """
    u = n
    s = n + 1
    while u < s:
        s = u
        t = (k - 1) * s + n // pow(s, k - 1)
        u = t // k
    return s


def choose_nf_m(d):
    """Choose parameters nf (sieve of factor base) and m (for sieving
    in [-m,m].
    """
    # Using similar parameters as msieve-1.52
    if d <= 34:
        return 200, 65536
    if d <= 36:
        return 300, 65536
    if d <= 38:
        return 400, 65536
    if d <= 40:
        return 500, 65536
    if d <= 42:
        return 600, 65536
    if d <= 44:
        return 700, 65536
    if d <= 48:
        return 1000, 65536
    if d <= 52:
        return 1200, 65536
    if d <= 56:
        return 2000, 65536 * 3
    if d <= 60:
        return 4000, 65536 * 3
    if d <= 66:
        return 6000, 65536 * 3
    if d <= 74:
        return 10000, 65536 * 3
    if d <= 80:
        return 30000, 65536 * 3
    if d <= 88:
        return 50000, 65536 * 3
    if d <= 94:
        return 60000, 65536 * 9
    return 100000, 65536 * 9
