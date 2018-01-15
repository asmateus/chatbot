"""
APIs often return messages in specific formats:
    xml, json, csv.
This module is to be used by apis for such generic
formats, in specific cases, best is to implement
a different parser in each api class.
"""


def parse_cvs(data, separator=','):
    data = data.split()  # split at \n\r
    keys = data[0].split(separator)

    # Accept only one column
    return {k: v for k, v in zip(keys, data[1].split(separator))}


def parse_xml(data):
    pass
