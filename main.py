from generator import generate_factorizers_dict
from statistics import average_of_factorizers

if __name__ == "__main__":
    factorizer_dict = generate_factorizers_dict([32, 64])
    result = average_of_factorizers(factorizer_dict, 1)

    print("test")
