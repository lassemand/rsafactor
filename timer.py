import time


def factorization_timer(factorizer):
    print("start timer")
    start_time = int(round(time.time() * 1000))
    factorizer.factorize();
    end_time = int(round(time.time() * 1000))
    print("end timer")
    return end_time - start_time
