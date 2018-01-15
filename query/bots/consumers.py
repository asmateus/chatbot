"""
Consumers definition module.
The different kinds of querybots (consumers) are
defined here. All consumers inherit from RabbitConsumer
and should define class level variables:
    TYPE: matching types.Query.XX
    MSG_OK: message to render when the consumer
            finishes successfully.
    MSG_EMPTY: message to render when API data is not
               significant.
A callback needs to be implemented and is called
when the channel of the matching type of the bot
has a message.
Upon successful finish, bots redistribute the message
to the client using redistribute function, through a
special channel:
    channel: redistribution-<client-username>

Warning: For safety reasons do not execute this module
         directly, use the spawner.
Note: Two types of error are handled:
      1. Not recognized body format
      2. Exception during execution
"""


import argparse
import pika
import sys

from . import types
from . import apis


def redistribute(client, message):
    queue = 'redistribution-' + client

    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message)
    connection.close()


class _RabbitConsumer:
    TYPE = None
    MSG_OK = ''
    MSG_EMPTY = 'No results from your query.'
    MSG_MALFORMED = 'Wrong query format.'
    MSG_ERROR = 'API unavailable.'
    MSG_NO_CLIENT = 'Client undetermined.'

    def __init__(self, consumer_type):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=consumer_type)
        self.channel.basic_consume(self.callback,
                                   queue=consumer_type,
                                   no_ack=True)
        self.client = ''

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        # Received a petition for a stock request
        self.client, company = self.handle_income_message(body)

        # If client is None, abort all
        if not self.client:
            print(self.MSG_NO_CLIENT)
            return

        if company:
            try:
                result = self.api.retreive(company)
                return_message = self.make_return_str(company, result)
            except Exception:
                # API is unsuitable
                redistribute(self.client, self.MSG.MSG_ERROR)
            else:
                redistribute(self.client, return_message)
        else:
            redistribute(self.client, self.MSG_MALFORMED)

    def make_return_str(self, api_data):
        raise NotImplementedError


class StockBot(_RabbitConsumer):
    TYPE = types.Query.STOCK
    MSG_OK = '%s quote is $%s per share.'

    def __init__(self):
        super(StockBot, self).__init__(StockBot.TYPE)
        self.api = apis.StockAPI()

        self.start_consuming()

    def handle_income_message(self, message):
        # message: of format username|company
        message = message.decode('utf-8')

        if len(message.split('|')) == 2:
            return message.split('|')
        return None, None

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

            return self.MSG_OK % (search, str_avg)
        except Exception:
            pass
        return self.MSG_EMPTY


class DayRangeBot(_RabbitConsumer):
    TYPE = types.Query.DAY_RANGE
    MSG_OK = '%s Days Low quote is $%s and Days High quote is $%s.'

    def __init__(self):
        super(DayRangeBot, self).__init__(DayRangeBot.TYPE)
        self.api = apis.DayRangeAPI()

        self.start_consuming()

    def handle_income_message(self, message):
        # message: of format username|company
        message = message.decode('utf-8')

        if len(message.split('|')) == 2:
            return message.split('|')
        return None, None

    def make_return_str(self, search, api_data):
        # This API returns a stock range for the day
        stock_high = api_data.get('High')
        stock_low = api_data.get('Low')

        if stock_high and stock_low:
            return self.MSG_OK % (search, stock_low, stock_high)
        return self.MSG_EMPTY


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
