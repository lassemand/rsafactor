import argparse
import rsa

from decimal import Decimal


def count_fraction_values(bits, rounds):
    key_counters = [0] * 100
    for index in range(rounds):
        (_, privkey) = rsa.newkeys(bits)
        min_val = Decimal(min(privkey.p, privkey.q))
        sqrt_val = Decimal(privkey.n).sqrt()
        interval = int((min_val / sqrt_val) * Decimal(100))
        key_counters[interval] += 1
    return key_counters

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rounds', type=int, help='number of rounds to be tested')
    parser.add_argument('--bits', type=int, help='size of the security parameter k')
    args = parser.parse_args()
    if args.rounds is None:
        args.rounds = 100000
    if args.bits is None:
        args.bits = 2048
    fractions_count = count_fraction_values(args.bits, args.rounds)
