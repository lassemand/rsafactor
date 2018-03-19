import pika
import json
import uuid

number_of_trials = {}
p, q = 2, 3

def initiate_pollard_rho_parallel(trial_n, n, k, a, ips, server_ip):
    data = {'trial_n': trial_n, 'n': n, 'k': k, 'a': a, 'ips': ips, 'server_ip': server_ip}
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()

    correlation_id = str(uuid.uuid1())
    number_of_trials[correlation_id] = 0
    channel.basic_publish(exchange='',
                          routing_key='pollard_rho_parallel',
                          properties=pika.BasicProperties(
                              headers={'correlation_id': correlation_id} # Add a key/value header
                          ),
                          body=json.dumps(data))
    connection.close()


def create_pollard_rho_parallel_return_queue(server_ip):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()


    def callback(ch, method, properties, body):
        global number_of_trials, p, q
        correlation_id = properties.headers['correlation_id']
        if correlation_id not in number_of_trials:
            return
        data = json.loads(body)
        p = data['p']
        if p != 1 and p != data['n']:
            q = int(data['n'] / p)
            channel.stop_consuming()
        else:
            number_of_trials[correlation_id] += 1
            if len(data['ips']) == number_of_trials[correlation_id]:
                initiate_pollard_rho_parallel(data['trial_n'], data['n'], 1, data['a'] + 1, data['ips'], data['server_ip'])

    channel.basic_consume(callback,
                          queue='pollard_rho_parallel_result',
                          no_ack=True)
    channel.start_consuming()
    connection.close()
    return p, q
