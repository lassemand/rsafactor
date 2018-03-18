import pika


def initiate_pollard_rho_parallel(ips, ):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pollard_rho_parallel')

    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
    print(" [x] Sent 'Hello World!'")
    connection.close()
