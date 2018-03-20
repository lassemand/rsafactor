#!/usr/bin/env python
import json
import math
import random
import numpy as np

import pika


def build_poly(roots):
    if len(roots) == 0:
        return [1]
    else:
        roots.sort()
        p = np.array([[-r, 1] for r in roots], dtype=object)
        n = len(p)
        while n > 1:
            m, r = divmod(n, 2)
            tmp = [polymul(p[i], p[i+m]) for i in range(m)]
            if r:
                tmp[0] = polymul(tmp[0], p[-1])
            p = tmp
            n = m
        p = p[0][::-1]
        if len(roots) & 1:
            p = [val * (-1) for val in p]
        return p


def polymul(c1, c2):
    ret = np.convolve(c1, c2)
    return trimseq(ret)


def trimseq(seq):
    if len(seq) == 0:
        return seq
    else:
        for i in range(len(seq) - 1, -1, -1):
            if seq[i] != 0:
                break
        return seq[:i+1]


def polyval(p, x):
    y = 0
    for i in range(len(p)):
        y = y * x + p[i]
    return y


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
        print("xs_i: " + str(xs[i]))
        print("ys_i" + str(ys[i]))
        polynomial = build_poly(ys[i])
        print("polynomial: " + str(polynomial))
        for x in xs[i]:
            Q *= polyval(polynomial, x)
            print("Q: " + str(Q))
    return Q


def compute_values_callback(ch, method, properties, body):
    print("compute_values_callback")
    data = json.loads(body)
    X, Y = compute_values(data['trial_n'], data['n'], data['k'], data['a'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=data['server_ip']))
    channel = connection.channel()
    data['X'] = X
    data['Y'] = Y
    print(X)
    print(Y)
    channel.basic_publish(exchange='', routing_key='pollard_rho_parallel_setup',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': properties.headers['correlation_id']}
                          ),
                          body=json.dumps(data))
    connection.close()


def compute_q_callback(ch, method, properties, body):
    print("compute_q_callback")
    data = json.loads(body)
    print(data['X'])
    print(data['Y'])
    Q = correlation_product(data['X'], data['Y'])
    p = math.gcd(Q, data['n'])
    data['p'] = p
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=data['server_ip']))
    channel = connection.channel()
    channel.basic_publish(exchange='',
                          routing_key='pollard_rho_parallel_result',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': properties.headers['correlation_id']}
                          ),
                          body=json.dumps(data))
    connection.close()


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel_worker_setup')
    channel.queue_declare(queue='pollard_rho_parallel_worker_correlation_product')


    channel.basic_consume(compute_values_callback,
                          queue='pollard_rho_parallel_worker_setup',
                          no_ack=True)

    channel.basic_consume(compute_q_callback,
                          queue='pollard_rho_parallel_worker_correlation_product',
                          no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
