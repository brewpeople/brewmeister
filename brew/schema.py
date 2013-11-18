import json
from pkg_resources import resource_string


def loads(path):
    """Read schema and return a string"""
    return resource_string(__name__, path).decode('utf-8')


def loadd(path):
    """Read schema and return a dict"""
    return json.loads(loads(path))
