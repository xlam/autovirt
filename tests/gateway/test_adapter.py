from typing import Protocol


class Adapter(Protocol):
    def fetch(self, num: int) -> list[dict]:
        ...


class Api:
    def __init__(self):
        self._s = "api"

    def fetch(self, num: int) -> list[dict]:
        return [{"num": num, "s": self._s}, {"num": num, "s": self._s}]


class ApiMock:
    def __init__(self):
        self._s = "mock"

    def fetch(self, num: int) -> list[dict]:
        return [{"num": num, "s": self._s}, {"num": num, "s": self._s}]


class Gateway:
    def __init__(self, adapter: Adapter):
        self.adapter = adapter

    def get(self, num: int) -> list[dict]:
        return self.adapter.fetch(num)


def test_adapter():
    gw = Gateway(ApiMock())
    print(gw.get(5))
