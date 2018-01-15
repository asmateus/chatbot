'''
    Automation of database setup (migrations and filling default values), and other
    configurations that should be performed prior to the usage of the application
'''
import subprocess
import django
import json
import string
import random
import os


def random_key():
    return ''.join([random.SystemRandom().choice("{}{}{}".format(
        string.ascii_letters, string.digits, string.punctuation)) for i in range(50)])


# Default configs
CONFIGS = {
    'DJANGO_SECRET_KEY': random_key(),
    'PIKA_CONNECTION_PARAMETERS': 'localhost',
    'BOT_NAME': 'emily',
    'BOT_EMAIL': 'emily@localhost',
    'BOT_PASSWORD': '123456',
}

# Check if configuration file exist, if not, create it
PATH = os.path.expanduser('~/.chatbot/')
CONFIG_FILE = 'configs.json'

if not os.path.exists(PATH + CONFIG_FILE):
    # Check if directory exists
    if not os.path.exists(PATH):
        os.makedirs(PATH, exist_ok=True)

    with open(PATH + CONFIG_FILE, 'w+') as conf_file:
        json.dump(CONFIGS, conf_file)


# Database setup. Three processes will be performed, in order
# make migrations -> apply migrations -> fill database (default info)
CMDS = [
    ('Creating migrations... ', 'python manage.py makemigrations chat'),
    ('Migrating... ', 'python manage.py migrate')]

for info, cmd in CMDS:
    print(info, end='')
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print('DONE!')

# Create a user for the bot
# For that load django environment
# Set up django variables (Fixes errors when using the models)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

# Load configs
configs = {}

with open(PATH + CONFIG_FILE, 'r') as fconfigs:
    configs = json.load(fconfigs)

bot_user = User.objects.create_user(
    username=configs.get('BOT_NAME'),
    email=configs.get('BOT_EMAIL'),
    password=configs.get('BOT_PASSWORD'),
)
bot_user.save()
