from generator import generate_factorizers_dict
from persistance import sqlite_persistance
from statistics import average_of_factorizers
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bits', required=True, type=int, nargs='+',
                        help='bits to be executed')
    parser.add_argument('--rounds', required=True, type=int, help='number of rounds to be executed')
    parser.add_argument('--method', help='method to be used')
    parser.add_argument('--processes', type=int, help='number of processes to be used')
    args = parser.parse_args()

    if args.processes is None:
        args.processes = 3
    persistance = sqlite_persistance()
    for _ in range(args.rounds):
        factorizer_dict = generate_factorizers_dict(args.bits, args.method, args.processes)
        result = average_of_factorizers(factorizer_dict)
        persistance.save_statistics(result, args.method)
