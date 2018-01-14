import pika


class RabbitConsumer:
    def __init__(self, consumer_type):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=consumer_type)
        self.channel.basic_consume(self.callback, queue=consumer_type,
                                   no_ack=True)
        self.start_consuming()

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print('Received', body)


if __name__ == '__main__':
    RabbitConsumer('/stock')
