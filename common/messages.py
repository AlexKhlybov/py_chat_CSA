# action - PRESENCE
def action_presence(user):
    """Функция формирует сообщение PRESENCE"""
    msg = {
        "action": "presence",
        "time": "<unix timestamp>",
        "type": "status",
        "user": {"account_name": user, "status": "Yep, I am here!"},
    }
    return msg


# action - AUTH
def action_auth(user):
    """Функция формирует сообщение AUTH"""
    msg = {
        "action": "authenticate",
        "time": "<unix timestamp>",
        "user": {"account_name": user, "password": "Secret"},
    }
    return msg


# action - MSG
def action_msg(alias, message, to="#all"):
    """Функция формирует сообщение MSG"""
    msg = {"action": "msg", "time": "<unix timestamp>", "to": to, "from": alias, "message": message}
    return msg


# action - JOIN
def action_join(alias, room):
    """Функция формирует сообщение JOIN"""
    msg = {"action": "join", "time": "<unix timestamp>", "from": alias, "room": room}
    return msg


# action - LEAVE
def action_leave(room):
    """Функция формирует сообщение LEAVE"""
    msg = {"action": "leave", "time": "<unix timestamp>", "room": room}
    return msg


# action - QUIT
def action_quit():
    """Функция формирует сообщение QUIT"""
    msg = {"action": "quit"}
    return msg
