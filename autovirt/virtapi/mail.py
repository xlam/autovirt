import time
from typing import Optional

from autovirt import utils
from autovirt.mail.interface import MailGateway
from autovirt.session import VirtSession
from autovirt.structs import Message

logger = utils.get_logger()


class VirtMailGateway(MailGateway):

    default_box = "system"

    def __init__(self, session: VirtSession):
        self.s = session

    def _fetch_messages(self, box: str):
        r = self.s.get(
            f"https://virtonomica.ru/api/vera/main/user/message/browse?box={box}"
        )
        data = r.json()["data"]
        return data

    def get_messages(
        self, subject: str = None, box: Optional[str] = None
    ) -> list[Message]:
        box = box if box else self.default_box
        data = self._fetch_messages(box)
        if not data:
            return []
        messages = list(data.values())
        if subject:
            messages = [
                message for message in messages if message["subject"] == subject
            ]
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

    def delete_messages(self, messages: list[Message], box: Optional[str] = None):
        for message in messages:
            box = box if box else self.default_box
            url = (
                f"https://virtonomica.ru/api/vera/main/user/message/del"
                f"?message_id={message.id}"
                f"&box={box}"
                f"&token={self.s.token}"
            )
            logger.info(f"deleting message {message.id} ({message.subject})")
            time.sleep(1)
            self.s.get(url)
