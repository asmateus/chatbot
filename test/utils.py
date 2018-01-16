import pika


class _RabbitConsumer:
    def __init__(self, queue, total):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(self.callback,
                                   queue=queue,
                                   no_ack=True)
        self.messages = []
        self.total = total

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.messages.append(body.decode('utf-8'))

        if len(self.messages) == self.total:
            self.channel.stop_consuming()

    def make_return_str(self, api_data):
        raise NotImplementedError


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
