# action - PROBE
def action_probe():
    """Формирует и возвращает сообщение PROBE"""
    msg = {"action": "probe", "time": "<unix timestamp>"}
    return msg


# action - MSG
def action_msg(message, to="#all"):
    """Функция формирует сообщение MSG"""
    msg = {"action": "msg", "time": "<unix timestamp>", "to": to, "from": "srv", "message": message}
    return msg


def msg_err(num, alert):
    msg = {"response": num, "time": "<unix timestamp>", "alert": alert}
    return msg


def get_101(msg):
    return msg_err(101, msg)


def get_102(msg):
    return msg_err(102, msg)


def get_200():
    return msg_err(200, "ОК")


def get_201(obj):
    return msg_err(201, f"{obj} успешно создан")


def get_400():
    return msg_err(400, "Неправильный запрос/JSON-объект")


def get_401():
    return msg_err(401, "Не авторизован")


def get_402():
    return msg_err(402, "Неправильный логин/пароль")


def get_404():
    return msg_err(404, "Пользователь/чат отсутствует на сервере")


def get_409():
    return msg_err(409, "Пользователь/чат отсутствует на сервере")
