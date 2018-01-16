import pika


class _RabbitProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def post_query(self, query, message):
        """
        Create a queue for the query.
        """
        body = message
        self.channel.queue_declare(queue=query)
        self.channel.basic_publish(
            exchange='',
            routing_key=query,
            body=body)

    def close(self):
        self.connection.close()
