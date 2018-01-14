import json

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

import bots


@channel_session_user_from_http
def connect(message):
    # connect using the user of the session as the
    # Group identifier. This enables fowarding to
    # multiple instances of the same user

    if not message.user.is_authenticated:
        return

    # Add this particular socket to the Group <username>
    Group(message.user.username).add(message.reply_channel)

    # Accept connection
    # Handshake fails if no response is sent
    Group(message.user.username).send({'accept': True})


@channel_session_user
def receive(message):
    """
    Receive user command and trigger an answer
    mechanism. Answer time is not guaranteed,
    it depends on the bot type, and the command
    given.
    """
    if not message.user.is_authenticated:
        return

    # Select a bot to manage the message this
    # bot is only an interface, it delegates
    # the command to hidden decoupled bots.
    recipient = bots.BotFactory.new_available_interface()

    data = json.loads(message['text'])
    recipient.receive(
        user=message.user,
        message=data.get('message'),
        medium=Group(message.user.username))


@channel_session_user
def disconnect(message):
    Group(message.user.username).discard(message.reply_channel)
