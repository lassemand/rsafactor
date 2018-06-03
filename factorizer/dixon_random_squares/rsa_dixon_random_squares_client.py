import math

import pika
from interface import implements
import json
import uuid

from factorizer.dixon_random_squares.rsa_dixon_random_squares import factor_from_square
from factorizer.quadratic_sieve.matrix_operations import build_index_matrix, solve_matrix_opt
from factorizer.rsa_factorizer import rsa_factorizer
from helper.primes_sieve import primes_sieve



def send_initiate_request(server_ip, n, m, B, c):
    global correlation_id
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip, blocked_connection_timeout=3600, socket_timeout=3600))
    channel = connection.channel()
    queue_name = 'dixon_random_squares_parallel_initiate'
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': correlation_id}
                          ),
                          body=json.dumps({'n': n, 'm': m, 'B': B, 'c': c, 'size': 7}))
    connection.close()


class rsa_dixon_random_squares_client(implements(rsa_factorizer)):
    def __init__(self, n, e, m, server_ip):
        self.n = n
        self.e = e
        self.m = m
        self.server_ip = server_ip
        k = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = primes_sieve(k)

    def build_up_test_values_parallel(self, c):
        send_initiate_request(self.server_ip, self.n, self.m, self.B, c)
        queue_name = 'dixon_random_squares_parallel_smooth_relations'

        def smooth_relations_callback(ch, method, properties, body):
            global smooth_relations, binary_matrix
            data = json.loads(body)
            binary_matrix.extend(data['binary_matrix'])
            smooth_relations.extend(data['smooth_relations'])
            if len(binary_matrix) > len(self.B):
                channel.stop_consuming()
            else:
                send_initiate_request(self.server_ip, self.n, self.m, self.B, c)


        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(smooth_relations_callback,
                              queue=queue_name,
                              no_ack=True)
        channel.start_consuming()


    def factorize(self, c=1):
        global smooth_relations, binary_matrix, correlation_id
        correlation_id = str(uuid.uuid1())
        smooth_relations = []
        binary_matrix = []
        self.build_up_test_values_parallel(c)
        M_opt, M_n, M_m = build_index_matrix(binary_matrix)
        perfect_squares = solve_matrix_opt(M_opt, M_n, M_m)
        for square_indices in perfect_squares:
            p = factor_from_square(self.n, square_indices, smooth_relations)
            if p != 1 and p != self.n:
                break
        print("p:" + str(p))
        return p, int(self.n / p)

