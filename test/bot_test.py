from argparse import RawTextHelpFormatter
import subprocess as sp
import argparse
import sys
import time

from query import spawner
from .utils import _RabbitProducer


class ConnectionToRabbit:
    """
    Test idea:
            1. Create a simple producer
            2. Publish N messages to channel
            3. Start consumer
            4. Watch if channel got emptied
    """
    N = 2000
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
        time.sleep(1)

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

        # If 0 test was successful
        return total

    def check_queue_size(self, q):
        return self.producer.channel.queue_declare(queue=q).method.message_count


class MessageRedistribution:
    def __init__(self):
        pass

    def test(self):
        return 1


class MalformedQueryHandling:
    def __init__(self):
        pass

    def test(self):
        return 1


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
        print('----------', 'Test %s... ' % test, '----------')
        Test = tests[test]
        return_val = Test().test()

        if return_val == 0:
            print('----------', 'SUCCEEDED', '----------')
        else:
            print('----------', 'FAILED', '----------')


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
