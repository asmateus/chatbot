from argparse import RawTextHelpFormatter
import argparse
import sys

from query import spawner


class ConnectionToRabbit:
    """
    Test idea:
            1. Create a simple producer
            2. Publish N messages to channel
            3. Start consumer
            4. Watch if channel got emptied
    """
    N = 100

    def __init__(self):
        pass

    def test(self):
        return 1


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
        print('Test %s... ' % test, end='')
        Test = tests[test]
        return_val = Test().test()

        if return_val == 0:
            print('SUCCEEDED')
        else:
            print('FAILED')


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
