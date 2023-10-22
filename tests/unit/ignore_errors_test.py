from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.application.log_proxies.converter import IgnoreErrorsProxy


class ConverterMock:
    def convert(self, tdata: Tdata) -> Session:
        raise ValueError("some error")


class LoggerMock:
    def __init__(self):
        self.last_message: str | None = None

    def error(self, message: str):
        self.last_message = message


def test_ignore_errors():
    logger = LoggerMock()
    converter = IgnoreErrorsProxy[Tdata, Session](ConverterMock(), logger)

    try:
        converter.convert(Tdata(path=""))

    except AccountBannedException:
        pass

    else:
        assert False, "Got no error after conversion"

    assert logger.last_message == "Error converting from Tdata, ValueError: some error"
