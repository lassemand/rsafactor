
import pika
import json
from interface import implements

from factorizer.rsa_factorizer import rsa_factorizer


class rsa_pollard_rho_parallel(implements(rsa_factorizer)):
    def __init__(self, n, e, m, k_calculator, n_calculator, worker_ips, server_ip):
        self.n = n
        self.e = e
        self.m = m
        self.k_calculator = k_calculator
        self.n_calculator = n_calculator
        self.worker_ips = worker_ips
        self.server_ip = server_ip
        self.processed_results = 0


    def result_received(self, ch, method, properties, body):
        print('result_recieved')
        data = json.loads(body)
        if data['p'] != 1 and data['p'] != self.n:
            ch.stop_consuming()
        else:
            self.processed_results += 1

        if self.processed_results == self.m:
            self.processed_results = 0
            ch.basic_publish(exchange='pollard_rho_initiate', routing_key='', body=json.dumps({'server_ip': data['server_ip'], 'n': data['n'], 'k':1, 'a': data['a'] + 2, 'trial_n': data['trial_n'], 'worker_ips': self.worker_ips}))

    def factorize(self):
        global xs, ys
        trial_n = self.n_calculator.calculate(self.n, self.m, 1)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))
        channel = connection.channel()
        channel.basic_publish(exchange='pollard_rho_parallel_setup', routing_key='', body=json.dumps({'server_ip': self.server_ip, 'n':self.n, 'k':1, 'a':1, 'trial_n': trial_n, 'worker_ips': self.worker_ips}))
        channel.queue_declare(queue='pollard_rho_parallel_result')
        channel.basic_consume(self.result_received,
                          queue='pollard_rho_parallel_result',
                          no_ack=True)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

class advanced_n_calculator:
    def __init__(self, k):
        self.k = k
    def calculate(self, n, m, k):
        # The extra m is added to ensure that m divides n
        return int(m * (n ** (1/4) // m ** 2))
