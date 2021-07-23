import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from datetime import datetime as dt
from common.variables import *
from common.codes import Code
from common.request_body import BaseBody


class BasePackage:
    __slots__ = (TIME, TYPE)

    def __init__(self):
        super().__init__()
        self.time = dt.timestamp(dt.now())

    def get_dict(self):
        return {s: getattr(self, s, None) for s in self.__slots__}


class Request(BasePackage):
    __slots__ = (ACTION, BODY, TIME, TYPE)

    def __init__(self, action, body=''):
        super().__init__()
        self.type = REQUEST
        self.action = action
        self.body = body

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[ACTION], json_obj[BODY])
        if TIME in json_obj:
            ins.time = json_obj[TIME]
        return ins

    def get_dict(self):
        d = super().get_dict()
        b = d[BODY]
        if b and isinstance(b, BaseBody):
            d[BODY] = (d[BODY]).get_dict()
        return d

    def __str__(self):
        return f'REQUEST  | {str(self.get_dict())}'

    def __eq__(self, other):
        if not isinstance(other, Request):
            return False
        if other.action != self.action:
            return False
        if other.body != self.body:
            return False
        if other.time != self.time:
            return False
        return True


class Response(BasePackage):
    __slots__ = (CODE, MESSAGE, TIME, TYPE)

    def __init__(self, code, message=None):
        super().__init__()
        self.type = RESPONSE
        self.code = code.code
        if message:
            self.message = message
        else:
            self.message = code.message

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(Code(json_obj[CODE], json_obj[MESSAGE]))
        if TIME in json_obj:
            ins.time = json_obj[TIME]
        return ins

    def __str__(self):
        return f'RESPONSE | {str(self.get_dict())}'

    def __eq__(self, other):
        if not isinstance(other, Response):
            return False
        if other.code != self.code:
            return False
        if other.message != self.message:
            return False
        if other.time != self.time:
            return False
        return True