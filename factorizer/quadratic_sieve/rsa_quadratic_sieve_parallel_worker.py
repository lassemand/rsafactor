import argparse

import pika
from math import sqrt, log2
import json

from factorizer.quadratic_sieve.rsa_quadratic_sieve import find_first_polynomial, find_next_poly, sieve_factor_base, \
    TRIAL_DIVISION_EPS, trial_divide


def trial_division(n, sieve_array, factor_base, g, h, m, smooth_relations):
    limit = log2(m * sqrt(n)) - TRIAL_DIVISION_EPS
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            gx = g.eval(x)
            divisors_idx = trial_divide(gx, factor_base)
            if divisors_idx is not None:
                u = h.eval(x)
                v = gx
                smooth_relations.append((u, v, divisors_idx))


def find_smooth_relations(n, m, factor_base):
    i_poly = 0
    smooth_relations = []
    while i_poly < 2 ** (len(B) - 1):
        if i_poly == 0:
            g, h, B = find_first_polynomial(n, m, factor_base)
        else:
            g, h = find_next_poly(n, factor_base, i_poly, g, B)
        i_poly += 1

        sieve_array = sieve_factor_base(factor_base, m)
        trial_division(
            n, sieve_array, factor_base, smooth_relations,
            g, h, m)
    return smooth_relations

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue_name', required=True, help='unique extension of the queue name')
    parser.add_argument('--server_ip', required=True, help='ip of the server')
    args = parser.parse_args()
    quadratic_sieve_initiate_name = 'quadratic_sieve_parallel_initiate'
    quadratic_sieve_queue_name = quadratic_sieve_initiate_name + args.queue_name
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.server_ip))
    channel = connection.channel()

    channel.queue_declare(queue=quadratic_sieve_queue_name)
    channel.queue_declare(queue='quadratic_sieve_parallel_smooth_relations')
    channel.exchange_declare(exchange=quadratic_sieve_initiate_name, exchange_type='fanout')
    channel.queue_bind(exchange=quadratic_sieve_initiate_name, queue=quadratic_sieve_queue_name)


def callback(ch, method, properties, body):
    data = json.loads(body)
    smooth_relations = find_smooth_relations(data['n'], data['m'], data['factor_base'])
    channel.basic_publish(exchange='',
                          routing_key='quadratic_sieve_parallel_smooth_relations',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': properties.headers['correlation_id']}
                          ),
                          body=json.dumps(smooth_relations))
    channel.basic_consume(callback, queue=quadratic_sieve_queue_name, no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
