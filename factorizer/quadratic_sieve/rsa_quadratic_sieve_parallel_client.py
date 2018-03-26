import uuid

import pika
import json

smooth_relations = []
active_correlation_id = None


def initiate_quadratic_sieve_parallel(server_ip, n, m, factor_base):
    global active_correlation_id
    data = {'n': n, 'm': m, 'factor_base': factor_base}
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()
    active_correlation_id = str(uuid.uuid1())
    queue_name = 'quadratic_sieve_parallel_initiate'
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': active_correlation_id, 'request_type':1}  # Add a key/value header
                          ),
                          body=json.dumps(data))
    connection.close()


def send_new_request(server_ip, correlation_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()
    queue_name = 'quadratic_sieve_parallel_initiate'
    channel.basic_publish(exchange=queue_name,
                          routing_key='',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': correlation_id, 'request_type':2}  # Add a key/value header
                          ),
                          body='{}')
    connection.close()


def retrieve_smooth_relations(server_ip, required_relations):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()
    queue_name = 'quadratic_sieve_parallel_smooth_relations'
    channel.queue_declare(queue=queue_name)

    def smooth_relations_callback(ch, method, properties, body):
        global smooth_relations, active_correlation_id
        correlation_id = properties.headers['correlation_id']
        if active_correlation_id != correlation_id:
            return

        smooth_relations.extend(json.loads(body))

        if required_relations <= len(smooth_relations):
            channel.stop_consuming()
        else:
            send_new_request(server_ip, correlation_id)

    channel.basic_consume(smooth_relations_callback,
                          queue=queue_name,
                          no_ack=True)
    channel.start_consuming()
    return smooth_relations

if __name__ == "__main__":
    retrieve_smooth_relations('localhost', 100)
