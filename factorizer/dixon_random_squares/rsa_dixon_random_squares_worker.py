import argparse
import json

import math
import pika

from factorizer.dixon_random_squares.rsa_dixon_random_squares import factorize_number_from_primes

j = 0
current_uuid = None


def build_up_congruence_values(c, n, size, B, pad, m):
    global j
    smooth_relations = []
    binary_matrix = []
    while len(smooth_relations) < size:
        j = j + 1
        Z = math.ceil(math.sqrt((j*m + pad) * n)) + c
        Z_squared = int(Z ** 2 % n)
        factorized_binary_number_row = factorize_number_from_primes(Z_squared, B)
        if factorized_binary_number_row is not None:
            smooth_relations.append((Z, Z_squared))
            binary_matrix.append(factorized_binary_number_row)
    return smooth_relations, binary_matrix


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue_name', required=True, help='unique extension of the queue name')
    parser.add_argument('--server_ip', required=True, help='ip of the server')
    parser.add_argument('--pad', required=True, type=int, help='integer to pad with')
    args = parser.parse_args()
    pad = args.pad
    dixon_random_squares_initiate_name = 'dixon_random_squares_parallel_initiate'
    dixon_random_squares_queue_name = dixon_random_squares_initiate_name + args.queue_name
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.server_ip))
    channel = connection.channel()
    channel.queue_declare(queue=dixon_random_squares_queue_name)
    channel.exchange_declare(exchange=dixon_random_squares_initiate_name, exchange_type='fanout')
    channel.queue_bind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)


    def callback(ch, method, properties, body):
        global j, current_uuid
        corr_id = properties.headers['correlation_id']
        if current_uuid is None or current_uuid != corr_id:
            print("Reset")
            j = 0
            current_uuid = corr_id
        data = json.loads(body)
        channel.queue_unbind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)
        smooth_relations, binary_matrix = build_up_congruence_values(data['c'], data['n'], data['size'], data['B'], pad, data['m'])
        channel.queue_bind(exchange=dixon_random_squares_initiate_name, queue=dixon_random_squares_queue_name)
        channel.basic_publish(exchange='',
                              routing_key='dixon_random_squares_parallel_smooth_relations',
                              body=json.dumps({'smooth_relations': smooth_relations, 'binary_matrix': binary_matrix}))
    channel.basic_consume(callback, queue=dixon_random_squares_queue_name, no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
