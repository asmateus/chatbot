from argparse import RawTextHelpFormatter
import subprocess as sp
import argparse
import sys
import time

from query import spawner
from .utils import _RabbitProducer, _RabbitConsumer


class ConnectionToRabbit:
    """
    Test idea:
            1. Create a simple producer
            2. Publish N messages to channel
            3. Start consumer
            4. Watch if channel got emptied
    """
    N = 100
    QUEUES = ['/stock', '/day_range']

    def __init__(self):
        self.producer = _RabbitProducer()

    def test(self):
        print('Creating dummy commands...')
        for q in self.QUEUES:
            print(q + ':', end=' ')
            for i in range(self.N):
                self.producer.post_query(q, 'APPL')
            print(self.check_queue_size(q))

        print('Spawning consumers...')
        worker_pids = spawner.Spawner.spawn()

        # Wait for workers
        time.sleep(2)

        # Stop workers
        for pid in worker_pids:
            print('Killing consumer', pid)
            p = sp.Popen(['kill', str(pid)])
            p.wait()

        # Check if queues are empty
        total = 0
        for q in self.QUEUES:
            total += self.check_queue_size(q)

        print('Commands left', total)
        print('Closing...')
        self.producer.close()

        # If 0 test was successful
        return total

    def check_queue_size(self, q):
        return self.producer.channel.queue_declare(queue=q).method.message_count


class MessageRedistribution:
    """
    Test idea:
            1. Create a simple producer
            2. Publish N messages to channel
            3. Start consumer
            4. Check redistribution channel
    """
    N = 10
    QUEUES = ['/stock', '/day_range']

    def __init__(self):
        self.producer = _RabbitProducer()

    def test(self):
        print('Creating dummy commands...')
        for q in self.QUEUES:
            print(q + ':', end=' ')
            for i in range(self.N):
                self.producer.post_query(q, 'testing-suite|APPL')
            print(self.check_queue_size(q))

        print('Spawning consumers...')
        worker_pids = spawner.Spawner.spawn()

        # Wait for workers
        time.sleep(10)

        # Stop workers
        for pid in worker_pids:
            print('Killing consumer', pid)
            p = sp.Popen(['kill', str(pid)])
            p.wait()

        # Check if queues are empty
        print('Checking redistribution queue: redistribution-testing-suite...')
        result = self.check_queue_size('redistribution-testing-suite')

        print('Commands in redistribution queue', result)
        print('Deleting redistribution queue...')
        self.producer.channel.queue_delete(queue='redistribution-testing-suite')
        print('Closing...')
        self.producer.close()

        if result == len(self.QUEUES) * self.N:
            return 0
        return 1

    def check_queue_size(self, q):
        return self.producer.channel.queue_declare(queue=q).method.message_count


class MalformedQueryHandling:
    """
    Test idea:
            1. Create a simple producer
            2. Publish 1 malformed queries and 1 good query
            3. Start consumers
            4. Check redistribution channel
            5. Consume from redistribution channel
            6. Check messages
    """
    QUEUES = ['/stock', '/day_range']
    QUERIES = ['testing-suite|', 'testing-suite|APPL']
    MSG_MALFORMED = 'Wrong query format.'

    def __init__(self):
        self.producer = _RabbitProducer()

    def test(self):
        print('Creating 1 malformed and 1 good query per queue...')
        for q in self.QUEUES:
            print(q + ':', end=' ')
            for m in self.QUERIES:
                self.producer.post_query(q, m)
            print(self.check_queue_size(q))

        print('Spawning consumers...')
        worker_pids = spawner.Spawner.spawn()

        # Wait for workers
        time.sleep(10)

        # Stop workers
        for pid in worker_pids:
            print('Killing consumer', pid)
            p = sp.Popen(['kill', str(pid)])
            p.wait()

        # Fetch messages from redistribution queue
        print('Fetching messages from redistribution-testing-suite')

        total_to_read = self.check_queue_size('redistribution-testing-suite')
        consumer = _RabbitConsumer('redistribution-testing-suite', total_to_read)
        consumer.start_consuming()

        mal_sent = 1 * len(self.QUEUES)
        good_sent = 1 * len(self.QUEUES)
        malformed_count = consumer.messages.count(self.MSG_MALFORMED)
        good_count = len(consumer.messages) - malformed_count
        print('Detected', malformed_count, 'of', mal_sent, 'malformed queries sent.')
        print('Detected', good_count, 'of', good_sent, 'good queries sent.')

        print('Deleting redistribution queue...')
        self.producer.channel.queue_delete(queue='redistribution-testing-suite')
        print('Closing...')
        self.producer.close()

        if malformed_count == mal_sent and good_count == good_sent:
            return 0
        return 1

    def check_queue_size(self, q):
        return self.producer.channel.queue_declare(queue=q).method.message_count


class EmptyAPIResponse:
    def __init__(self):
        pass

    def test(self):
        return 1


class CorrectResponseFormat:
    def __init__(self):
        pass

    def test(self):
        return 1


def start_tests(tests, t_type=''):
    if not isinstance(tests, dict):
        tests = {t_type: tests}
    for test in tests:
        test_str = '--- Test %s... ' % test
        print(test_str, '-' * (90 - 1 - len(test_str)))
        Test = tests[test]
        return_val = Test().test()

        if return_val == 0:
            print('-' * 90, 'SUCCEEDED')
        else:
            print('-' * 90, 'FAILED')


TESTS_SUPPORTED = {
    'connection_to_rabbit': ConnectionToRabbit,
    'message_redistribution': MessageRedistribution,
    'malformed_query_handling': MalformedQueryHandling,
    'empty_api_response': EmptyAPIResponse,
    'correct-response-format': CorrectResponseFormat,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test Suite for bots',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-t', help=('Test selection, empty for all tests.'
                                    + 'Supported tests are:\n'
                                    + '\n'.join(T for T in TESTS_SUPPORTED)))

    test_selected = parser.parse_args().t

    if not test_selected:
        test = TESTS_SUPPORTED
    else:
        test = TESTS_SUPPORTED.get(test_selected)

    if not test:
        print('No valid test selected.')
        sys.exit(1)

    start_tests(test, t_type=test_selected)
