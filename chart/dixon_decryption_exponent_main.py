import argparse

import matplotlib.pyplot as plt
import random

from persistance import sqlite_persistance

def generate_random_chart_color(index):
    return ['b', 'g', 'r', 'c', 'm', 'y', 'k'][index]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, type=str, help='name of the file to be saved')
    args = parser.parse_args()
    persistance = sqlite_persistance()
    types = ['dixon_random_square_0.4', 'dixon_random_square_0.6', 'dixon_random_square_0.8', 'dixon_random_square_1.0', 'brute_force']
    stats = persistance.retrieve_statistics(types)
    plt.yscale('log')
    for (index, stat) in enumerate(stats):
        plt.plot(stat[0], stat[1], color=generate_random_chart_color(index), label='test')
        plt.legend()
    plt.xticks(list(set([item for sublist in [s[0] for s in stats] for item in sublist])))
    plt.ylabel('Execution time')
    plt.xlabel('Key size in bits')
    plt.savefig(args.name)