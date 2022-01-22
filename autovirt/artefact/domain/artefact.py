from autovirt.structs import Message


def build_innovations_renewal_list(messages: list[Message]) -> list:
    renewal = []
    for message in messages:
        for attach in message.attaches:
            renewal.append(attach)
    return renewal
