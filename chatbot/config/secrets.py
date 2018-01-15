"""
Small utility module for loading private information.
Loads configs.json from:
    ~/.chatbot/configs.json
In that order. Otherwise, it falls back to some default
value.
"""

__all__ = ['DJANGO_SECRET_KEY']

import json
import os

__TRY_PATHS = [os.path.expanduser('~/.chatbot/')]
__CONFIG_FILE = 'configs.json'


def __parse_config_file():
    for path in __TRY_PATHS:
        configs = {}
        try:
            with open(path + __CONFIG_FILE, 'r') as fconfigs:
                configs = json.load(fconfigs)
        except Exception:
            # File does not exist or
            # File corrupted
            continue
        else:
            return configs
    return configs


__configs = __parse_config_file()

DJANGO_SECRET_KEY = __configs.get('DJANGO_SECRET_KEY') or ''
