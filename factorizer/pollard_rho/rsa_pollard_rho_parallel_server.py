#!/usr/bin/env python
import pika
import json

# Declare this variable because Rabbitmq does not guarantee no dublicates
processed_ids = set()
processed_Xs = {}
processed_Ys = {}


def callback_pollard_rho(ch, method, properties, body):
    global processed_ids, processed_Xs, processed_Ys
    print("callback_pollard_rho")
    correlation_id = properties.headers['correlation_id']
    if correlation_id in processed_ids:
        return
    processed_ids.add(correlation_id)
    data = json.loads(body)
    for ip in data['ips']:
        print("sent message to: " + ip)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
        channel = connection.channel()
        channel.basic_publish(exchange='',
                              routing_key='pollard_rho_parallel_worker_setup',
                              properties=pika.BasicProperties(
                                  headers={'correlation_id': correlation_id} # Add a key/value header
                              ),
                              body=body)
        connection.close()
    processed_Xs[correlation_id] = [[] for _ in range(data['trial_n'])]
    processed_Ys[correlation_id] = [[] for _ in range(data['trial_n'])]


def callback_setup_pollard_rho(ch, method, properties, body):
    global processed_ids, processed_Xs, processed_Ys
    print("callback_setup_pollard_rho")
    data = json.loads(body)
    correlation_id = properties.headers['correlation_id']
    processed_X = processed_Xs[correlation_id]
    processed_Y = processed_Ys[correlation_id]
    X = data['X']
    Y = data['Y']
    for i in range(data['trial_n']):
        processed_X[i].append(X[i])
        processed_Y[i].append(Y[i])
    m = len(data['ips'])
    if len(processed_X[0]) != m:
        return
    indexes = [((u * data['trial_n']) // m, (((u + 1) * data['trial_n']) // m) - 1) for u in range(m)]
    print("trial_n: " + str(data['trial_n']))
    print("m: " + str(len(data['ips'])))
    saved_args = [(processed_X[index[0]:index[1]], processed_Y[index[0]:index[1]]) for index in indexes]
    for (index, ip) in enumerate(data['ips']):
        data_to_be_processed = saved_args[index]
        data['X'] = data_to_be_processed[0]
        data['Y'] = data_to_be_processed[1]
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
        channel = connection.channel()
        channel.basic_publish(exchange='',
                              properties=pika.BasicProperties(
                                  headers={'correlation_id': correlation_id}
                              ),
                              routing_key='pollard_rho_parallel_worker_correlation_product',
                              body=json.dumps(data))
        connection.close()


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