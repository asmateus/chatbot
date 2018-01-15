import random
import threading
import json
import re
import pika
import datetime

from django.contrib.auth.models import User

from chat import helpers
from chat import models

from . import types
from .generic_answers import ANSWERS


class BotFactory:
    _INTERFACES = ['shinobu']

    @staticmethod
    def new_available_interface() -> '_Interface':
        # There is no requirement for a specific
        # interface so, get the first one.
        return _Interface(BotFactory._INTERFACES[0])


class RedistributionListener:
    """
    Listen to result from workers
    """
    TIMEOUT = 10

    def __init__(self, interface, queue):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(self.callback, queue=queue,
                                   no_ack=True)
        self.connection.add_timeout(self.TIMEOUT, self.on_timeout)

        self.interface = interface

        # Instead of stop consuming upon callback,
        # let callback be repeatedly called to empty
        # the queue of possible stale messages.
        # Finally timing out gracefully by the
        # accomplished flag.
        self.accomplished = False
        self.start_consuming()

    def on_timeout(self):
        self.channel.stop_consuming()

        if not self.accomplished:
            self.interface.on_worker_result('It took me too long... sorry.')
        else:
            print('Graceful exit')

    def start_consuming(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.accomplished = True
        self.interface.on_worker_result(body.decode('utf-8'))


class _RabbitProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def post_query(self, query, message, username):
        """
        Create a temporal queue for the query.
        body: of format username|message.
        message: of format query=company.
        username: needed for the redistribution queue.
        """
        body = username + '|' + message.replace(query + '=', '')
        self.channel.queue_declare(queue=query)
        self.channel.basic_publish(
            exchange='',
            routing_key=query,
            body=body)
        self.connection.close()


class _Interface(_RabbitProducer):
    def __init__(self, name):
        super(_Interface, self).__init__()
        # Lock until a user is found
        self.__locked = True

        # An interface requires an associated user
        self.user = None
        try:
            self.user = User.objects.get(username=name)
        except User.DoesNotExist:
            print(name, 'interface failed to start.')
        else:
            self.__locked = False

    def receive(self, user, message, medium):
        """
        Receive and interpret message.
        Spawn bot if required
        """
        if self.__locked:
            return

        self.client = user
        self.medium = medium

        query = self.__query_of(message)
        if query is None:
            # User did not issue a query, simulate
            # intelligent chat and save to db
            self.__answer_and_store(message)
            return

        # Message was a special command
        self.post_query(query, message, self.client.username)
        self.__await_result()

    def on_worker_result(self, result):
        msg = self.__make_message(result)

        # Message is not saved so, manual creation of
        # timestamp is needed
        msg.created_at = datetime.datetime.now()

        self.__send_back(msg)

    def __await_result(self):
        listen_thread = threading.Thread(
            target=RedistributionListener,
            args=(self, 'redistribution-' + self.client.username))
        listen_thread.start()

    def __query_of(self, message):
        exp = '^QUERY='
        for query in types.ALL_QUERIES:
            regex = exp.replace('QUERY', query)

            if re.search(regex, message) is not None:
                return query

    def __pick_answer(self):
        return random.choice(ANSWERS[self.user.username])

    def __make_message(self, message, incoming=False):
        origin, target = self.user, self.client

        if incoming:
            origin = self.client
            target = self.user

        msg = models.Message(
            origin=origin,
            target=target,
            content=message,
        )
        return msg

    def __answer_and_store(self, message):
        # Just pick an answer randomly,
        # this is a simulation
        answer = self.__pick_answer()

        # Transform to message model
        incoming_msg = self.__make_message(message, incoming=True)
        answer_msg = self.__make_message(answer)

        incoming_msg.save()
        answer_msg.save()

        # Send both back, so that chat is consistent
        self.__send_back(incoming_msg)
        self.__send_back(answer_msg)

    def __send_back(self, message):
        self.medium.send({'text': json.dumps({
            'created_at': helpers.date_of(message.created_at),
            'username': message.origin.username,
            'message': message.content,
        })})
