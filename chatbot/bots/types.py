""" Types of queries to match. Each should resemble a specific bot.
"""


class Query:
    STOCK = '/stock'
    DAY_RANGE = '/day_range'


ALL_QUERIES = [Query.__dict__[attr]
               for attr in Query.__dict__ if not attr.startswith('__')]
