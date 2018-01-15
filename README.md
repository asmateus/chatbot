# Financial Chat Bot
Financial chat bot is a simple conversation bot that supports user management and conversation storage. A simple front-end interface is offered to easy interaction.

## Requirement checklist
The requirements of the project are as follows:

- [x] Have persistent users with profiles (it may imply user creation, login, logout)
- [x] Have a message history and order them by timestamp (order direction assumed as most recent first)
- [x] Make the history accessible from the profile (other sites also accessible)
- [x] Show only 50 last messages (as a bonus a `limit_to=#` parameter can be passed to the get request to modify the limit, -1 means no limit)
- [x] Handle commands `/stock=<>` and `/day_range=<>` from the user (in the chatroom) differently
- [x] Special commands launch decoupled bots to retreive data from an API (different from bot to bot)
- [x] Bot will reply back to the user when the result is available
- [x] Special commands and bot responses are not saved to database
- [ ] Test what should be tested
- [x] Provide error handling for bots

## Design specifications
The financial chatbot, given the requirements, is composed of two independent packages. They can, and should, be executed independently as different processes. The packages are:

    chatbot/
    query/
    
`chatbot` holds the webserver in charge of user interaction, it exposes the user to its stored data. Given the nature of the project (a chat), a real time connection based on web sockets was selected, using **Django** + **Django Channels**.

`query` is a package in charge of spawning background workers that listen to the RabbitMQ server, retreive data from external APIs and post them back to the server. Bots are implemented using **pika**, a lightweight manager for RabbitMQ, and **requests** for API information retrieval.

Currently the project is simple enough for a SQLite database. Secret stuff like the `DJANGO_SECRET_KEY` should be placed in a separated file at `~/.chatbot/configs.json`. To test the project easily, the `setup` script will autogenerate a configuration file for you.

## Installation
The project requires the following Python packages to be installed (Python 3):

* Django
* pika
* channels
* requests
* asgi-redis

All of these are installed via `pip` (or `pip3` if the case), further more, a `requirements.txt` file is provided so install the packages via:

    pip install -r requirements.txt
    
Additionally the following applications are required:

* rabbitmq (see [this](https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-rabbitmq) to install)
* redis (easy install: `sudo apt-get install redis-server`)

Do not forget to start/enable the respective services. Finally, head to `chatbot` sub-directory and run the `setup` script:

    python setup.py
    
This will create configuration files, make database migrations and create a user for our bot.

## Usage
To start the bots (from the project root directory):
    
    python -m query.spawner

To start the webserver (from the project root directory):

    cd chatbot
    python manage.py runserver

Then go to the following url and interact with the application as you see convenient:

    http://localhost:8000/chat

The following directions are available to you:

|                   URL                   |       Site     |
|:---------------------------------------:| :--------------: |
| `http://localhost:8000/` | Chat Room |
| `http://localhost:8000/chat/` | Chat Room |
| `http://localhost:8000/login/` | Login form |
| `http://localhost:8000/logout/` | Logout request |
| `http://localhost:8000/create-user/` | Create user form |
| `http://localhost:8000/u/<username>/` | Profile page |
| `http://localhost:8000/u/<username>/profile/` | Profile page |
| `http://localhost:8000/u/<username>/profile-edit/` | Profile edition page |
| `http://localhost:8000/u/<username>/history/` | History page |
