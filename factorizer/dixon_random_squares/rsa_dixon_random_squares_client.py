import math

import pika
import time
from interface import implements
import numpy as np
import json

from factorizer.dixon_random_squares.rsa_dixon_random_squares import factor_from_reduced_matrix
from factorizer.rsa_factorizer import rsa_factorizer
from helper.gaussian_elimination import reduced_row_echelon_form
from helper.primes_sieve import primes_sieve


def send_initiate_request(server_ip, n, m, B, c):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()
    queue_name = 'dixon_random_squares_parallel_initiate'
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          body=json.dumps({'n': n, 'm': m, 'B': B, 'c': c}))
    connection.close()


class rsa_dixon_random_squares_client(implements(rsa_factorizer)):
    def __init__(self, n, e, m, server_ip, test_congruence):
        self.n = n
        self.e = e
        self.m = m
        self.server_ip = server_ip
        k = int(math.exp(0.5 * math.sqrt(math.log1p(self.n) * math.log1p(math.log1p(self.n)))))
        self.B = primes_sieve(k)
        self.test_congruence = test_congruence

    def build_up_test_values_parallel(self, c):
        send_initiate_request(self.server_ip, self.n, self.m, self.B, c)
        queue_name = 'dixon_random_squares_parallel_smooth_relations'

        def smooth_relations_callback(ch, method, properties, body):
            global smooth_relations, Z, completed_processes, smooth_binary_relations
            data = json.loads(body)
            Z.extend(data['Z'])
            smooth_relations.extend(data['rows_in_factor'])
            smooth_binary_relations.extend(data['rows_in_binary_factor'])
            completed_processes += 1
            if completed_processes == self.m:
                channel.stop_consuming()

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.basic_consume(smooth_relations_callback,
                              queue=queue_name,
                              no_ack=True)
        channel.start_consuming()
        return np.array(Z), np.array(smooth_relations), np.array(smooth_binary_relations)

    def factorize(self, c=1):
        global smooth_relations, Z, completed_processes, smooth_binary_relations
        completed_processes = 0
        Z = []
        smooth_relations = []
        smooth_binary_relations = []
        Z, all_rows_in_factor, all_rows_in_binary_factor = self.build_up_test_values_parallel(c)
        matrix, numpivots = reduced_row_echelon_form(all_rows_in_binary_factor.transpose())
        start_time = int(round(time.time() * 1000))
        ones = np.array(
            [[index for (index, bit) in enumerate(matrix[i, :]) if bit] for i in reversed(range(numpivots))])
        p, q = factor_from_reduced_matrix(ones, self.test_congruence, Z, all_rows_in_factor, np.array(self.B, dtype=int), self.n)
        end_time = int(round(time.time() * 1000))
        print("Factor: " + str(end_time - start_time))
        if p is not None and q is not None:
            return p, q
        return self.factorize(c + self.m)
