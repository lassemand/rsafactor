#!/usr/bin/env python
import argparse
import json
import math
import random
import numpy as np

import pika


def build_poly(roots):
    p = np.array([[r, -1] for r in roots], dtype=object)
    while len(p) > 1:
        m, r = divmod(len(p), 2)
        tmp = [np.convolve(p[i], p[i+m]) for i in range(m)]
        if r:
            tmp[0] = np.convolve(tmp[0], p[-1])
        p = tmp
    p = p[0][::-1]
    return p


def trimseq(seq):
    if len(seq) == 0:
        return seq
    else:
        for i in reversed(range(len(seq))):
            if seq[i] != 0:
                break
        return seq[:i+1]


def polyval(p, x):
    y = 0
    for i in range(len(p)):
        y = y * x + p[i]
    return y


def compute_values_and_send_to_ip(trial_n, n, k, a, worker_ips, server_ip):
    f = lambda u: (u ** (2 * k) + a) % n
    X = []
    Y = []
    x = random.randint(2, n - 1)
    y = x
    progress_counter = 0
    for _ in range(trial_n):
        x = f(x)
        y = f(f(y))
        X.append(x)
        Y.append(y)
        if len(X) >= (trial_n / len(worker_ips)):
            ip = worker_ips[progress_counter]
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
            channel = connection.channel()
            channel.basic_publish(exchange='',
                                  routing_key='pollard_rho_parallel_computations',
                                  body=json.dumps({'X': X, 'Y': Y, 'n': n, 'server_ip':server_ip}))
            connection.close()
            X = []
            Y = []


def correlation_product(xs, ys):
    Q = 1
    for i in range(len(xs)):
        polynomial = build_poly(ys[i])
        for x in xs[i]:
            Q *= polyval(polynomial, x)
    return Q


X = []
Y = []
counter = 0
m = 0


def compute_result_callback(ch, method, properties, body):
    global counter, X, Y, m
    data = json.loads(body)
    counter += 1
    temp_x = data['X']
    temp_y = data['Y']
    for i in range(len(X)):
        x = temp_x[i]
        y = temp_y[i]
        X[i].append(x)
        Y[i].append(y)

    if counter == m:
        counter = 0
        Q = correlation_product(X, Y)
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


def compute_values_callback(ch, method, properties, body):
    global m, X, Y
    print("compute_values_callback")
    print(body)
    data = json.loads(body)
    compute_values_and_send_to_ip(data['trial_n'], data['n'], data['k'], data['a'], data['worker_ips'], data['server_ip'])
    X = [[] for _ in range(int(data['trial_n'] / len(data['worker_ips'])))]
    Y = [[] for _ in range(int(data['trial_n'] / len(data['worker_ips'])))]
    m = len(data['worker_ips'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_ip', help='server_ip of parallel implementation')
    args = parser.parse_args()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.server_ip))
    channel = connection.channel()
    channel.exchange_declare(exchange='pollard_rho_parallel_setup', exchange_type='fanout')
    channel.queue_declare(queue='pollard_rho_parallel_worker_setup')
    channel.queue_declare(queue='pollard_rho_parallel_computations')
    channel.queue_bind(exchange='pollard_rho_parallel_setup', queue='pollard_rho_parallel_worker_setup')
    channel.basic_consume(compute_values_callback,
                          queue='pollard_rho_parallel_worker_setup',
                          no_ack=True)
    channel.basic_consume(compute_result_callback,
                          queue='pollard_rho_parallel_computations',
                          no_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
