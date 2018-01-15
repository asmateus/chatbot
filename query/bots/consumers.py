import argparse
import pika
import sys

from . import types
from . import apis


def redistribute(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='redistribution')
    channel.basic_publish(
        exchange='',
        routing_key='redistribution',
        body=message)
    connection.close()


class _RabbitConsumer:
    TYPE = None
    MSG_OK = ''
    MSG_ERROR = ''

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
        raise NotImplementedError

    def make_return_str(self, api_data):
        raise NotImplementedError


class StockBot(_RabbitConsumer):
    TYPE = types.Query.STOCK
    MSG_OK = '%s quote is $%s per share.'
    MSG_ERROR = 'No results from your query.'

    def __init__(self):
        super(StockBot, self).__init__(StockBot.TYPE)
        self.api = apis.StockAPI()

        self.start_consuming()

    def callback(self, ch, method, properties, body):
        # Received a petition for a stock request
        body = body.decode('utf-8')
        result = self.api.retreive(body)

        return_message = self.make_return_str(body, result)
        redistribute(return_message)

    def make_return_str(self, search, api_data):
        # This API returns a stock average
        stock_high = api_data.get('High')
        stock_open = api_data.get('Open')
        stock_close = api_data.get('Close')
        stock_low = api_data.get('Low')

        # Try calculating OHLC average
        try:
            so, sh, sl, sc = map(float,
                                 [stock_open, stock_high, stock_low, stock_close])
            average = (so + sh + sl + sc) / 4

            # Convert to string, with 2 significant figures
            str_avg = str(round(average, 2))

            return StockBot.MSG_OK % (search, str_avg)
        except Exception:
            return StockBot.MSG_ERROR


class DayRangeBot(_RabbitConsumer):
    TYPE = types.Query.DAY_RANGE
    MSG_OK = '%s Days Low quote is $%s and Days High quote is $%s.'
    MSG_ERROR = 'No results from your query.'

    def __init__(self):
        super(DayRangeBot, self).__init__(DayRangeBot.TYPE)
        self.api = apis.DayRangeAPI()

        self.start_consuming()

    def callback(self, ch, method, properties, body):
        # Received a petition for a stock request
        body = body.decode('utf-8')
        result = self.api.retreive(body)

        return_message = self.make_return_str(body, result)
        redistribute(return_message)

    def make_return_str(self, search, api_data):
        # This API returns a stock range for the day
        stock_high = api_data.get('High')
        stock_low = api_data.get('Low')

        if stock_high and stock_low:
            return DayRangeBot.MSG_OK % (search, stock_low, stock_high)
        return DayRangeBot.MSG_ERROR


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
