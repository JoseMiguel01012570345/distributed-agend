import json
from enum import Enum

class Color(Enum):
    
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    
    pass


def set_json_data_to_send(data,encoding='utf-8'):
    json_data = json.dumps(data)
    return bytes(json_data,encoding)

def get_data_from_json(data_bytes):
    json_data = data_bytes.decode()
    return json.loads(json_data)

def inbettwen(key,under_quote,over_quote):
    if under_quote < over_quote:
        return key > under_quote and key < over_quote
    return key > under_quote or key < over_quote