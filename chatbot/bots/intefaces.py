import random
import json
import re
import pika

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


class _RabbitProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

    def post_query(self, query, message):
        # Queue is only created once, afterwards this
        # does nothing, unless a different query is used.
        self.channel.queue_declare(queue=query)
        self.channel.basic_publish(
            exchange='',
            routing_key=query,
            body=message.replace(query + '=', ''))
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
        self.post_query(query, message)

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
