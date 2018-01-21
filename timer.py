import time


def factorization_timer(factorizer):
    start_time = int(round(time.time() * 1000))
    factorizer.factorize();
    end_time = int(round(time.time() * 1000))
    return end_time - start_time
