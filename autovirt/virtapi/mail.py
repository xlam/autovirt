import time

from autovirt import utils
from autovirt.structs import Message
from autovirt.session import VirtSession


logger = utils.get_logger()
s = VirtSession()


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
            f"&token={s.token}"
        )
        logger.info(f"deleting message {message.id} ({message.subject})")
        time.sleep(1)
        s.get(url)
