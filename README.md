# Financial Chat Bot
Financial chat bot is a simple conversation bot that supports user management and conversation storage. A simple front-end interface is offered to easy interaction.

## Requirement checklist
The requirements of the project are as follows

- [x] Have persistent users with profiles (it may imply user creation, login, logout)
- [x] Have a message history and order them by timestamp (order direction assumed as most recent first)
- [x] Make the history accessible from the profile (other sites also accessible)
- [x] Show only 50 last messages (as a bonus a `limit_to=#` parameter can be passed to the get request to modify the limit, -1 means no limit)
- [x] Handle commands `/stock=<>` and `/day_range=<>` from the user (in the chatroom) differently
- [x] Special commands launch decoupled bots to retreive data from an API (different from bot to bot)
- [x] Bot will reply back to the user when the result is available
- [x] Special commands and bot responses are not saved to database
- [ ] Test what should be tested
- [ ] Provide error handling for bots

## Installation
Make sure you install the following:

* Django
* pika
* RabbitMQ Server

The source code does not come with database migrations applied, so, to successfully start the chat, make sure to run the `setup.py` script in the `chatbot` sub-directory.

## Configuration
There is no need to configure anything, as the source code you received contains the configuration file `configs.json` at `chatbot/config`. However this is an edge case, the application normally searches first the `/opt/chatbot/` directory for such a configuration file. This file is private, and is included in the `.gitignore`.

## Usage
Once in the `chatbot` root directory, head to the sub-directory `chatbot` and start the Django server:

    cd chatbot
    python manage.py runserver

Then go to the following url and interact with the application as you see convenient:

    http://localhost:8000/chat

Optional: You can use `curl` to emulate the requests, in `extra` there are some commands with their explanation.

## Testing
In the `test` module are unit tests and functionality tests for several parts of the application,
you can go there and see what you can test, or simply run all the testbed with:

    python -m test.complete
