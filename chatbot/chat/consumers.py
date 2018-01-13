from channels import Group
from channels.sessions import channel_session
from .models import Message, User
import json


@channel_session
def ws_connect(message):
    print('connecting')
    prefix, username = message['path'].strip('/').split('/')
    Group('chat-' + username).add(message.reply_channel)
    Group('chat-' + username).send({'accept': True})
    message.channel_session['username'] = username


@channel_session
def ws_receive(message):
    print('receiving')
    username = message.channel_session['username']
    data = json.loads(message['text'])

    message = Message(
        origin=User.objects.get(username=username),
        target=User.objects.get(username='shinobu'),
        content=data.get('message')
    )
    message.save()

    Group('chat-' + username).send({'text': json.dumps(
        {
            'created_at': '2018-01-13',
            'username': 'shinobu',
            'message': 'Hello sir, how may I help you?'
        }
    )})


@channel_session
def ws_disconnect(message):
    print('disconnecting')
    username = message.channel_session['username']
    Group('chat-' + username).discard(message.reply_channel)
