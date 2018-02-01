from timer import factorization_timer


def average_of_x_rounds(factorizer, rounds=10):
    results = [None] * rounds
    for index in range(rounds):
        results[index] = factorization_timer(factorizer)
    return results


def average_of_factorizers(factorizers_dict, rounds=10):
    results = {}
    for key, value in factorizers_dict.items():
        results[key] = average_of_x_rounds(value, rounds)
    return results



