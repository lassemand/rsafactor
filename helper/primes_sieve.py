import numpy as np
import math


def primes_sieve(limit):
    limit = limit + 1
    not_prime = [False] * limit
    primes = []
    for i in range(2, limit):
        if not_prime[i]:
            continue
        for f in range(i * 2, limit, i):
            not_prime[f] = True
        primes.append(i)
    return primes

def is_even(i):
    return i % 2 == 0

def is_odd( i):
    return not is_even(i)

def make_odd(i, delta):
    assert delta in (-1, 1)
    return i if is_odd(i) else i + delta



def seg_sieve_primes(seg_range):
    # Segmented Sieve of Sieve of Eratosthenes finds primes in a range.

    # As in sieve_primes(), only odd numbers are tracked (evens are nonprime)
    # So first adjust the start/end of the segement so they're odd numbers, then
    # map into the sieve as follows: [seg_start, seg_start+1*2...seg_start+n*2]
    seg_start, seg_end = seg_range
    seg_start = make_odd(seg_start, +1)
    seg_end   = make_odd(seg_end,   -1)
    seg_len   = seg_end - seg_start + 1
    sieve_len = (seg_len + 1) // 2      # only track odds; evens nonprime
    sieve = np.ones(sieve_len, dtype=np.bool)

    # Find a short list of primes used to strike out non-primes in the segment
    root_limit = int(math.sqrt(seg_end)) + 1
    root_primes = primes_sieve(root_limit)
    assert seg_len > root_limit

    for root_prime in root_primes:

        # find the first odd multiple of root_prime within the segment
        prime_multiple = seg_start - seg_start % root_prime
        while not( is_odd(prime_multiple) and (prime_multiple >= seg_start) ):
            prime_multiple += root_prime

        # strike all multiples of the prime in the range...
        sieve_start = (prime_multiple - seg_start) // 2
        sieve[sieve_start : sieve_len : root_prime] = False

        # ...except for the prime itself
        if seg_start <= root_prime <= seg_end:
            ix = (root_prime - seg_start) // 2
            sieve[ix] = True

    prime_indexes = np.nonzero(sieve)[0]
    primes  = 2 * prime_indexes.astype(np.int32) + seg_start
    return primes
