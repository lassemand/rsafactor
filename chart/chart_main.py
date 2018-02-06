import matplotlib.pyplot as plt
import random

from persistance import sqlite_persistance


def generate_random_chart_color():
    return ['b', 'g', 'r', 'c', 'm', 'y', 'k'][random.randint(0, 6)]


if __name__ == "__main__":
    persistance = sqlite_persistance()
    stats = persistance.retrieve_statistics()
    for (_, stat) in enumerate(stats):
        plt.plot(stat[0][0], stat[0][1], color=generate_random_chart_color(), label=stat[1])
        plt.legend()
    plt.xticks(list(set([item for sublist in [s[0][0] for s in stats] for item in sublist])))
    plt.yticks(list(set([item for sublist in [s[0][1] for s in stats] for item in sublist])))
    plt.ylabel('Execution time')
    plt.xlabel('Key size in bits')
    plt.savefig('used-time-chart')
