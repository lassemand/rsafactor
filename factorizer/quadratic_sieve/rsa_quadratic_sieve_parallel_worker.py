import argparse

import pika
from math import sqrt, log2
import json

from factorizer.quadratic_sieve.factor_base_prime import factor_base_prime
from factorizer.quadratic_sieve.rsa_quadratic_sieve_B_from_variable import rsa_quadratic_sieve_B_from_variable
from factorizer.quadratic_sieve.rsa_quadratic_sieve_smooth_relations import TRIAL_DIVISION_EPS, trial_divide, \
    find_next_poly, sieve_factor_base

requested_data = None


def trial_division(n, sieve_array, factor_base, g, h, m, smooth_relations):
    limit = log2(m * sqrt(n)) - TRIAL_DIVISION_EPS
    for (i, sa) in enumerate(sieve_array):
        if sa >= limit:
            x = i - m
            gx = g.eval(x)
            divisors_idx, a = trial_divide(gx, factor_base)
            if a == 1:
                u = h.eval(x)
                v = gx
                smooth_relations.append((u, v, divisors_idx))


def find_smooth_relations(n, m, factor_base):
    i_poly = 0
    smooth_relations = []
    is_reset = False
    while not is_reset:
        if i_poly == 0:
            g, h, B = rsa_quadratic_sieve_B_from_variable(n, m, factor_base).build()
        else:
            g, h = find_next_poly(n, factor_base, i_poly, g, B)
        i_poly += 1
        if i_poly >= 2 ** (len(B) - 1):
            i_poly = 0
            is_reset = True

        sieve_array = sieve_factor_base(factor_base, m)
        trial_division(
            n, sieve_array, factor_base,
            g, h, m, smooth_relations)
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
    channel.exchange_declare(exchange=quadratic_sieve_initiate_name, exchange_type='fanout')
    channel.queue_bind(exchange=quadratic_sieve_initiate_name, queue=quadratic_sieve_queue_name)


    def callback(ch, method, properties, body):
        global requested_data
        channel.queue_unbind(exchange=quadratic_sieve_initiate_name, queue=quadratic_sieve_queue_name)
        data = json.loads(body)
        requst_type = properties.headers['request_type']
        if requst_type == 2 and requested_data is None:
            print("I should never be here")
            return
        if requst_type == 1:
            print("Initial")
            requested_data = {'n' : data['n'], 'm' : data['m'], 'factor_base' : [factor_base_prime(factor[0], factor[1], factor[2]) for factor in data['factor_base']]}
        smooth_relations = find_smooth_relations(requested_data['n'], requested_data['m'], requested_data['factor_base'])

        channel.queue_bind(exchange=quadratic_sieve_initiate_name, queue=quadratic_sieve_queue_name)
        channel.basic_publish(exchange='',
                              routing_key='quadratic_sieve_parallel_smooth_relations',
                              properties=pika.BasicProperties(
                                  headers={'correlation_id': properties.headers['correlation_id']}
                              ),
                              body=json.dumps(smooth_relations))
    channel.basic_consume(callback, queue=quadratic_sieve_queue_name, no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
