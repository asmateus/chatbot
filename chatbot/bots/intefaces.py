"""
An interface is a bot user that:
1. manages user input via receive function
2. manages bot answers by an __await_message function
3. sends messages back to the user by __send_back function

An interface can be given a role through the name parameter,
each role matches a different bot user in the chat.
Currently only one role is supported.

Note: To keep the system from flooding in Threads, the
      __await_message spawns a temporal listener, e.g
      RedistributionListener that consumes the queue
      for 10 idle seconds. If the worker takes longer, its
      messages will still be stored in the queue and will
      be dispatched at the next request from the user.
"""

import random
import threading
import json
import re
import datetime

from django.contrib.auth.models import User

from chat import helpers
from chat import models

from . import types
from .entities import _RabbitProducer, RedistributionListener
from .generic_answers import ANSWERS


class BotFactory:
    _INTERFACES = ['emily']

    @staticmethod
    def new_available_interface() -> '_Interface':
        # There is no requirement for a specific
        # interface so, get the first one.
        return _Interface(BotFactory._INTERFACES[0])


class _Interface(_RabbitProducer):
    """
        _Interface is the front view of the automated
        system for the client. That is, it simulates
        a user and handles the user messages. When they
        are queries (special commands), it will push
        a RabbitMQ to the queue for the workers to work
        on, otherwise, it simulates 'intelligent' conversation.
    """

    def __init__(self, name):
        super(_Interface, self).__init__()
        # Lock until a user is found
        self.__locked = True

        # A user is required to interact in chat
        self.user = None
        try:
            self.user = User.objects.get(username=name)
        except User.DoesNotExist:
            print(name, 'interface failed to start.')
        else:
            self.__locked = False

    def receive(self, user, message, medium):
        """
        Receive and interpret message. Spawn bot if required
        user: django.contrib.auth.models.User
        message: str
        medium: channels.Group (for answer redirection)
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
        # This thread will die at 10 seconds of inactivity
        listen_thread = threading.Thread(
            target=RedistributionListener,
            args=(self, 'redistribution-' + self.client.username))
        listen_thread.start()

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

    def __query_of(self, message):
        # Look if message matches a query type
        exp = '^QUERY='
        for query in types.ALL_QUERIES:
            regex = exp.replace('QUERY', query)

            if re.search(regex, message) is not None:
                return query

    def __send_back(self, message):
        self.medium.send({'text': json.dumps({
            'created_at': helpers.date_of(message.created_at),
            'username': message.origin.username,
            'message': message.content,
        })})

    def __pick_answer(self):
        return random.choice(ANSWERS[self.user.username])
