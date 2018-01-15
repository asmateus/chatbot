import argparse
import pika
import sys

from . import types
from . import apis


class _RabbitConsumer:
    TYPE = None

    def __init__(self, consumer_type):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=consumer_type)
        self.channel.basic_consume(self.callback, queue=consumer_type,
                                   no_ack=True)

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print('Got here')
        raise NotImplementedError


class StockBot(_RabbitConsumer):
    TYPE = types.Query.STOCK

    def __init__(self):
        super(StockBot, self).__init__(StockBot.TYPE)
        self.api = apis.StockAPI()

        self.start_consuming()

    def callback(self, ch, method, properties, body):
        # Received a petition for a stock request
        result = self.api.retreive(body.decode('utf-8'))
        print(self, result)


class DayRangeBot(_RabbitConsumer):
    TYPE = types.Query.DAY_RANGE

    def __init__(self):
        super(DayRangeBot, self).__init__(DayRangeBot.TYPE)
        self.api = apis.DayRangeAPI()

        self.start_consuming()

    def callback(self, ch, method, properties, body):
        # Received a petition for a stock request
        result = self.api.retreive(body.decode('utf-8'))
        print(self, result)


if __name__ == '__main__':
    ALL_WORKERS = [DayRangeBot, StockBot]

    parser = argparse.ArgumentParser(
        description='Launch workers by type')
    parser.add_argument(
        '-t', metavar='T', type=str, nargs='+', help='Worker type to launch')

    worker_type = parser.parse_args().t[0]

    # Launch the corresponding worker
    consumer_to_launch = None
    for Consumer in ALL_WORKERS:
        if Consumer.TYPE == worker_type:
            consumer_to_launch = Consumer
            break

    if consumer_to_launch is None:
        sys.exit(1)
    consumer_to_launch()
