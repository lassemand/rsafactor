import pika
import json


def initiate_pollard_rho_parallel(trial_n, n, k, a, ips, server_ip):
    data = {'trial_n': trial_n, 'n': n, 'k': k, 'a': a, 'ips': ips, 'server_ip': server_ip}
    json_data = json.dumps(data)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()

    channel.basic_publish(exchange='',
                      routing_key='pollard_rho_parallel',
                      body=json_data)


def create_pollard_rho_parallel_return_queue(server_ip):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_ip))
    channel = connection.channel()
    p, q = 2, 3

    def callback(ch, method, properties, body):
        p, q = 2, 3
        channel.stop_consuming()
    channel.basic_consume(callback,
                          queue='pollard_rho_parallel_result',
                          no_ack=True)
    channel.start_consuming()
    connection.close()
    print("test")


if __name__ == "__main__":
    p, q = create_pollard_rho_parallel_return_queue('localhost')
    print(p)
