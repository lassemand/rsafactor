import argparse
import json

import math
import pika
import numpy as np

from factorizer.dixon_random_squares.rsa_dixon_random_squares import factorize_number_from_primes


def build_up_congruence_values(c, n, size, B, pad, m):
    Z = []
    rows_in_factor = []
    rows_in_binary_factor = []
    j = 0
    i = 0
    while i < size:
        j = j + 1
        z = math.ceil(math.sqrt(int(j*m+pad) * n)) + c
        number = z ** 2 % n
        factorized_binary_number_row, factorized_number_row = factorize_number_from_primes(number, B)
        if factorized_number_row is not None:
            rows_in_factor.append(factorized_number_row)
            rows_in_binary_factor.append(factorized_binary_number_row)
            Z.append(z)
            i = i + 1
    return Z, rows_in_factor, rows_in_binary_factor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue_name', required=True, help='unique extension of the queue name')
    parser.add_argument('--server_ip', required=True, help='ip of the server')
    parser.add_argument('--pad', required=True, type=int, help='integer to pad with')
    args = parser.parse_args()
    pad = args.pad
    print(pad)
    dixon_random_squares_initiate_name = 'dixon_random_squares_parallel_initiate'
    dixon_random_squares_queue_name = dixon_random_squares_initiate_name + args.queue_name
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.server_ip))
    channel = connection.channel()
    channel.queue_declare(queue=dixon_random_squares_queue_name)
    channel.exchange_declare(exchange=dixon_random_squares_initiate_name, exchange_type='fanout')
    channel.queue_bind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)


    def callback(ch, method, properties, body):
        data = json.loads(body)
        channel.queue_unbind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)
        Z, rows_in_factor, rows_in_binary_factor = build_up_congruence_values(data['c'], data['n'], data['size'], data['B'], pad, data['m'])
        channel.queue_bind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)
        channel.basic_publish(exchange='',
                              routing_key='dixon_random_squares_parallel_smooth_relations',
                              body=json.dumps({'Z': Z, 'rows_in_factor': rows_in_factor, 'rows_in_binary_factor': rows_in_binary_factor}))
    channel.basic_consume(callback, queue=dixon_random_squares_queue_name, no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
