import pika
import json


def initiate_pollard_rho_parallel(trial_n, n, k, a, ips, server_ip):
    data = {'trial_n': trial_n, 'n': n, 'k': k, 'a': a, 'ips': ips}
    json_data = json.dumps(data)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()

    channel.basic_publish(exchange='',
                      routing_key='pollard_rho_parallel',
                      body=json_data)


def create_pollard_rho_parallel_return_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel_result')

    def callback(ch, method, properties, body):
        return body['p'], body['q']

    channel.basic_consume(callback,
                          queue='pollard_rho_parallel_result',
                          no_ack=True)
    connection.close()
