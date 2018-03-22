import uuid

import pika
import json

smooth_relations = []

def initiate_quadratic_sieve_parallel(server_ip, n, m, factor_base):
    data = {'n': n, 'm':m, 'factor_base':factor_base}
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()

    correlation_id = str(uuid.uuid1())
    channel.exchange_declare(exchange='quadratic_sieve_parallel_initiate', exchange_type='fanout')
    channel.basic_publish(exchange='quadratic_sieve_parallel_initiate',
                          routing_key='',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': correlation_id} # Add a key/value header
                          ),
                          body=json.dumps(data))
    connection.close()

def smooth_relations_callback():
    print("callback")

def retrieve_smooth_relations(server_ip):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.server_ip))
    channel = connection.channel()

    channel.queue_declare(queue=quadratic_sieve_queue_name)
    channel.queue_declare(queue='quadratic_sieve_parallel_smooth_relations')
    return []
