from enum import Enum

class UIOperation(Enum):
    CREATE_EVENT = 0
    CREATE_USER = -1
    AUTHENTICATE_USER = -2
    GET_ALL_GROUPS = -3
    CREATE_GROUP = -4
    DELETE_GROUP = -5
    GET_AGENDS_BY_GROUP = -6
    CREATE_AGEND = -7
    DELETE_AGEND = -8
    GET_EVENTS = -9
    GET_EVENT_BY_ID = -10
    DELETE_EVENT = -11
    pass