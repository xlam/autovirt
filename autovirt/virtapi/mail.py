from datetime import time

from autovirt import utils
from autovirt.structs import Message


logger = utils.get_logger("virtapi.message")
s = utils.get_logged_session()
token = utils.get_token(s)


def get_messages(box: str = "system", subject=None) -> list[Message]:
    r = s.get(f"https://virtonomica.ru/api/vera/main/user/message/browse?box={box}")
    data = r.json()["data"]
    if not data:
        return []
    messages = list(data.values())
    if subject:
        messages = [message for message in messages if message["subject"] == subject]
    res = []
    for message in messages:
        attaches = []
        if message["attaches"]:
            attaches = list(message["attaches"].values())
        res.append(
            Message(
                int(message["id"]),
                message["subject"],
                message["body"],
                int(message["status"]),
                attaches,
            )
        )
    return res


def delete_messages(messages: list[Message], box: str = "system"):
    for message in messages:
        url = (
            f"https://virtonomica.ru/api/vera/main/user/message/del"
            f"?message_id={message.id}"
            f"&box={box}"
            f"&token={token}"
        )
        logger.info(f"deleting message {message.id} ({message.subject})")
        time.sleep(1)
        s.get(url)