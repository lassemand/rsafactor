from timer import factorization_timer

def average_of_factorizers(factorizers_dict):
    results = {}
    for key, value in factorizers_dict.items():
        results[key] = [factorization_timer(value)]
    return results



