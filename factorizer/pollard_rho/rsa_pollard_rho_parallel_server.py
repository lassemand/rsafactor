#!/usr/bin/env python
import pika
import json

if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        list_of_ips = data.pop('ips')
        for ip in list_of_ips:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
            channel = connection.channel()
            channel.basic_publish(exchange='',
                                  routing_key='pollard_rho_parallel_worker',
                                  body=json.dumps(data))
        print("Server received %r" % body)

    channel.basic_consume(callback,
                          queue='pollard_rho_parallel',
                          no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()