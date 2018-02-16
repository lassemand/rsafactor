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

