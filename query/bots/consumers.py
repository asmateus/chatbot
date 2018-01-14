import argparse
import pika

from . import types


class _RabbitConsumer:
    TYPE = None

    def __init__(self, consumer_type):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=consumer_type)
        self.channel.basic_consume(self.callback, queue=consumer_type,
                                   no_ack=True)
        # self.start_consuming()

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print('Received', body)


class StockBot(_RabbitConsumer):
    TYPE = types.Query.STOCK

    def __init__(self):
        super(StockBot, self).__init__(StockBot.TYPE)
        print(self)


class DayRangeBot(_RabbitConsumer):
    TYPE = types.Query.DAY_RANGE

    def __init__(self):
        super(DayRangeBot, self).__init__(DayRangeBot.TYPE)
        print(self)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Launch workers by type')
    parser.add_argument(
        '-t', metavar='T', type=str, nargs='+', help='Worker type to launch')

    worker_type = parser.parse_args().t[0]

    # Launch the corresponding worker
    
