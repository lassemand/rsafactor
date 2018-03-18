#!/usr/bin/env python
import json
import random

import math
import pika
from helper.polynomial_builder import build_poly, polyval


def compute_values(trial_n, n, k, a):
    f = lambda u: (u ** (2 * k) + a) % n
    X = []
    Y = []
    x = random.randint(2, n - 1)
    y = x
    for _ in range(trial_n):
        x = f(x)
        y = f(f(y))
        X.append(x)
        Y.append(y)
    return X, Y


def correlation_product(xs, ys):
    Q = 1
    for i in range(len(xs)):
        polynomial = build_poly(ys[i])
        for x in xs[i]:
            Q *= polyval(polynomial, x)
    return Q

def compute_values_callback(ch, method, properties, body):
    print("compute_values_callback")
    data = json.loads(body)
    X, Y = compute_values(data.trial_n, data.n, data.k, data.a)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=data.server_ip))
    channel = connection.channel()
    data['X'] = X
    data['Y'] = Y
    channel.basic_publish(exchange='', routing_key='pollard_rho_parallel_setup', body=json.dumps(data))
    connection.close()


def compute_q_callback(ch, method, properties, body):
    print("compute_q_callback")
    data = json.loads(body)
    Q = correlation_product(data.X, data.Y)
    p = math.gcd(Q, data.n)
    if p != 1 and p != data.n:
        content = {}
        content.p = p
        content.q = int(data.n / p)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=data.server_ip))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key='pollard_rho_parallel_result', body=json.dumps(content))
        connection.close()


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel_worker_setup')
    channel.queue_declare(queue='pollard_rho_parallel_worker_correlation_product')


    channel.basic_consume(compute_values_callback,
                          queue='pollard_rho_parallel_worker_setup',
                          no_ack=True)

    channel.basic_consume(compute_values_callback,
                          queue='pollard_rho_parallel_worker_correlation_product',
                          no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
