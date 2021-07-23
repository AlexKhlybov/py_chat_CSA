from math import pi
import re
from common.variables import *


class BaseBody:

    def get_dict(self):
        return {s: str(getattr(self, s, None)) for s in self.__slots__}


class User(BaseBody):
    __slots__ = (USERNAME,)

    def __init__(self, username):
        self.username = username

    def get_dict(self):
        return self.username

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        if other.username != self.username:
            return False
        return True

    def __str__(self):
        return self.username


class Room(BaseBody):
    __slots__=(ROOMNAME, SUBSCRIBERS)

    def __init__(self, roomname, subscribers):
        self.roomname = roomname
        self.subscribers = subscribers

    def get_dict(self):
        return self.subscribers

    def __str__(self):
        return f'{self.roomname} >>>>> {self.subscribers}'


class Msg(BaseBody):
    __slots__ = (SENDER, TO, TEXT)

    PATTERN_USER = r'@(?P<to>[\w\d]*)?(?P<message>.*)'
    

    def __init__(self, text, sender, to='ALL'):
        self.text = text
        self.sender = sender
        self.to = to

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[TEXT], json_obj[SENDER], json_obj[TO])
        return ins

    def parse_msg(self):
        to = 'ALL'
        msg = self.text

        if '@' in msg:
            match = re.match(self.PATTERN_USER, msg)
            to = match.group(TO)
            msg = match.group(MESSAGE)
        # elif '#' in msg:
        #     match = re.match(self.PATTERN_GROUP, msg)
        #     to = '#' + match.group(TO)
        #     msg = match.group(MESSAGE)

        self.to = to
        self.text = msg

    def __str__(self):
        return f'{self.sender} to @{self.to}: {self.text}'


class MsgRoom(Msg):

    PATTERN_GROUP = r'#(?P<to>[\w\d]*)?(?P<message>.*)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_msg(self):
        to = ''
        msg = self.text

        if '#' in msg:
            match = re.match(self.PATTERN_GROUP, msg)
            to = '#' + match.group(TO)
            msg = match.group(MESSAGE)

        self.to = to
        self.text = msg

    def __str__(self):
        return f'{self.sender} to {self.to}: {self.text}'

    
    