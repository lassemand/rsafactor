import argparse

import matplotlib.pyplot as plt
import random

from persistance import sqlite_persistance


def generate_random_chart_color(index):
    return ['b', 'g', 'r', 'c', 'm', 'y', 'k'][index]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--types', nargs='+', type=str, help='the factorizer type to be included into the plot')
    parser.add_argument('--name', required=True, type=str, help='name of the file to be saved')
    args = parser.parse_args()
    if args.types is None:
        args.types = ['brute_force']
    persistance = sqlite_persistance()
    stats = persistance.retrieve_statistics(args.types)
    for (index, stat) in enumerate(stats):
        plt.plot(stat[0], stat[1], color=generate_random_chart_color(index), label=args.types[index])
        plt.legend()
    plt.xticks(list(set([item for sublist in [s[0] for s in stats] for item in sublist])))
    plt.yticks(list(set([item for sublist in [s[1] for s in stats] for item in sublist])))
    plt.ylabel('Execution time')
    plt.xlabel('Key size in bits')
    plt.savefig(args.name)
