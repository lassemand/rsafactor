#!/usr/bin/env python
import pika
import json

# Declare this variable because Rabbitmq does not guarantee no dublicates
already_processed = False
processed_X = []
processed_Y = []
processed_ids = {}


def callback_pollard_rho(ch, method, properties, body):
    global already_processed, processed_X, processed_Y
    print("callback_pollard_rho")
    if already_processed:
        return
    already_processed = True
    data = json.loads(body)
    processed_X = [[] for _ in range(data.trial_n)]
    processed_Y = [[] for _ in range(data.trial_n)]
    for ip in data['ips']:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
        channel = connection.channel()
        channel.basic_publish(exchange='',
                              routing_key='pollard_rho_parallel_worker_setup',
                              body=json.dumps(data))
        connection.close()


def callback_setup_pollard_rho(ch, method, properties, body):
    global already_processed, processed_X, processed_Y
    print("callback_setup_pollard_rho")
    data = json.loads(body)
    for i in range(data.trial_n):
        processed_X[i].append(data.X[i])
        processed_Y[i].append(data.Y[i])
    m = len(data.ips)
    if len(processed_X[0]) != m:
        return
    indexes = [((u * data.trial_n) // m, (((u + 1) * data.trial_n) // m) - 1) for u in range(m)]
    saved_args = [(processed_X[index[0]:index[1]], processed_Y[index[0]:index[1]]) for index in indexes]
    for (index, ip) in enumerate(body.ips):
        data_to_be_processed = saved_args[index]
        data = {'X': data_to_be_processed[0], 'Y': data_to_be_processed[1], 'n': data.n}
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
        channel = connection.channel()
        channel.basic_publish(exchange='',
                              routing_key='pollard_rho_parallel_worker_correlation_product',
                              body=json.dumps(data_to_be_processed))
        connection.close()
    already_processed = False

    for ip in data['ips']:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
        channel = connection.channel()
        channel.basic_publish(exchange='',
                              routing_key='pollard_rho_parallel_worker',
                              body=json.dumps(data))


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel')
    channel.queue_declare(queue='pollard_rho_parallel_setup')
    channel.queue_declare(queue='pollard_rho_parallel_result')

    channel.basic_consume(callback_pollard_rho,
                          queue='pollard_rho_parallel',
                          no_ack=True)

    channel.basic_consume(callback_setup_pollard_rho,
                          queue='pollard_rho_parallel_setup',
                          no_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()