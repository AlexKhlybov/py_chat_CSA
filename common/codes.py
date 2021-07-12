from common.variables import CODE, MESSAGE


class Code:
    __slots__ = (CODE, MESSAGE)

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __eq__(self, other: int):
        return self.code == other

    def __int__(self):
        return self.code

    def __str__(self):
        return f'{self.code} - {self.message}'


# 1xx
BASIC = Code(100, 'Basic message')
ANSWER = Code(101, '')
# 2xx
OK = Code(200, 'OK')
CREATED = Code(201, 'Connected created')
# 4xx
INCORRECT_REQUEST = Code(400, 'Incorrect request / json')
NOT_FOUND = Code(404, 'User / chat is missing on the server')
CONFLICT = Code(409, 'User already connected')
# 5xx
SERVER_ERROR = Code(500, 'Server error')
SERVER_UNAVAILABLE = Code(503, 'Service Unavailable ')