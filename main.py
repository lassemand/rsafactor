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
    parser.add_argument('--server_ip', help='server_ip of parallel implementation')
    parser.add_argument('--worker_ips', nargs='*', help='worker_ip of parallel implementation')
    parser.add_argument('--quadratic_sieve_tactic', type=int, help='type of polynomial builder to use')
    args = parser.parse_args()

    if args.processes is None:
        args.processes = 3

    if args.server_ip is None:
        args.server_ip = 'localhost'

    if args.worker_ips is None:
        args.worker_ips = ['localhost']
    persistance = sqlite_persistance()
    for _ in range(args.rounds):
        factorizer_dict = generate_factorizers_dict(args.bits, args.method, args.processes, args.worker_ips, args.server_ip, args.quadratic_sieve_tactic)
        result = average_of_factorizers(factorizer_dict)
        persistance.save_statistics(result, args.method)
