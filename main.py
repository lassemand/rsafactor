from generator import generate_factorizers_dict
from persistance import sqlite_persistance
from statistics import average_of_factorizers

if __name__ == "__main__":
    factorizer_dict = generate_factorizers_dict([32])
    result = average_of_factorizers(factorizer_dict, 2)
    persistance = sqlite_persistance()
    persistance.save_statistics(result, "brute_force")
