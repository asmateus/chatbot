import requests

from . import parsers


class StockAPI:
    API = ('https://stooq.com/q/l/?s=', '&f=sd2t2ohlcv&h&e=csv​')
    KNOWN_CONVERSIONS = {
        'APPL': 'aapl.us'
    }

    def __init__(self):
        self.parse = parsers.parse_cvs

    def retreive(self, param, formatted=True):
        stock_of = StockAPI.KNOWN_CONVERSIONS.get(param) or param
        url = StockAPI.API[0] + stock_of + StockAPI.API[1]
        r = requests.get(url)

        if formatted:
            return self.parse(r.text)
        return r.text


class DayRangeAPI:
    API = ('https://stooq.com/q/l/?s=', '&f=sd2t2ohlcv&h&e=csv​')
    KNOWN_CONVERSIONS = {
        'APPL': 'aapl.us'
    }

    def __init__(self):
        self.parse = parsers.parse_cvs

    def retreive(self, param, formatted=True):
        stock_of = DayRangeAPI.KNOWN_CONVERSIONS.get(param) or param
        url = DayRangeAPI.API[0] + stock_of + DayRangeAPI.API[1]
        r = requests.get(url)

        if formatted:
            return self.parse(r.text)
        return r.text
