def parse_cvs(data, separator=','):
    data = data.split()  # split at \n\r
    keys = data.pop().split(separator)

    # Accept only one column
    return {k: v for k, v in zip(keys, data[0].split(separator))}


def parse_xml(data):
    pass
