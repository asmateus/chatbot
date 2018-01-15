"""
Types of querybots that can be spawned, ALL_QUERIES
is useful when you want to spawn all possible bots.
This module must be edited if a new query bot is created.

Warning: This module should be identical to the types module
         of chatbot, or any other entity that shares the
         RabbitMQ server. If it is not identical, at least
         the needed query types should match, as channels
         are matched through query types.
"""


class Query:
    STOCK = '/stock'
    DAY_RANGE = '/day_range'


ALL_QUERIES = [Query.__dict__[attr]
               for attr in Query.__dict__ if not attr.startswith('__')]
