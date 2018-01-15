""" RabbitMQ interactors.
"""


import pika


class RedistributionListener:
    """
    Listen to result from workers
    """
    TIMEOUT = 10

    def __init__(self, interface, queue):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(self.callback, queue=queue,
                                   no_ack=True)
        self.connection.add_timeout(self.TIMEOUT, self.on_timeout)

        self.interface = interface

        # Instead of stop consuming upon callback,
        # let callback be repeatedly called to empty
        # the queue of possible stale messages.
        # Finally timing out gracefully by the
        # accomplished flag.
        self.accomplished = False
        self.start_consuming()

    def on_timeout(self):
        self.channel.stop_consuming()

        if not self.accomplished:
            self.interface.on_worker_result('It took me too long... sorry.')
        else:
            print('Graceful exit')

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.accomplished = True
        self.interface.on_worker_result(body.decode('utf-8'))


class _RabbitProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def post_query(self, query, message, username):
        """
        Create a queue for the query.
        body: of format username|message.
        message: of format query=company.
        username: needed for the redistribution queue.
        """
        body = username + '|' + message.replace(query + '=', '')
        self.channel.queue_declare(queue=query)
        self.channel.basic_publish(
            exchange='',
            routing_key=query,
            body=body)
        self.connection.close()
