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
    parser.add_argument('--server_ip', nargs='*', help='server_ip of parallel implementation')
    parser.add_argument('--worker_ips', nargs='*', help='worker_ip of parallel implementation')
    args = parser.parse_args()

    if args.processes is None:
        args.processes = 3

    if args.server_ip is None:
        args.server_ip = '159.65.86.139'

    if args.worker_ips is None:
        args.worker_ips = ['167.99.85.42']
    persistance = sqlite_persistance()
    for _ in range(args.rounds):
        factorizer_dict = generate_factorizers_dict(args.bits, args.method, args.processes, args.worker_ips, args.server_ip)
        result = average_of_factorizers(factorizer_dict)
        persistance.save_statistics(result, args.method)
