import pytest

from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException
from src.application.decorators.convert_attempt_decorotor import ConvertAttemptDecorator


class ConverterWithAccountNotFoundExceptionMock:
    def convert(self, tdata: Tdata) -> Session:
        raise AccountNotFoundException("acc")


class ConverterWithAccountBannedExceptionMock:
    def convert(self, tdata: Tdata) -> Session:
        raise AccountBannedException("acc")


class ConverterAttemptMock:
    def __init__(self):
        self.errors = [
            AccountBannedException("acc"),
            ValueError("bla"),
        ]

    def convert(self, tdata: Tdata) -> Session:
        if self.errors:
            raise self.errors.pop()

        return Session(json_path="acc.json", session_path="acc.session")


def test_account_not_found():
    converter = ConvertAttemptDecorator[Tdata, Session](
        ConverterWithAccountNotFoundExceptionMock(), 3
    )

    with pytest.raises(AccountNotFoundException):
        converter.convert(Tdata("acc/tdata"))


def test_account_banned():
    converter = ConvertAttemptDecorator[Tdata, Session](
        ConverterWithAccountBannedExceptionMock(), 3
    )

    with pytest.raises(AccountBannedException):
        converter.convert(Tdata("acc/tdata"))


def test_convert_attempt():
    converter = ConvertAttemptDecorator[Tdata, Session](ConverterAttemptMock(), 3)

    session = converter.convert(Tdata("acc/tdata"))

    assert session.json_path == "acc.json"


def test_less_convert_attempt():
    converter = ConvertAttemptDecorator[Tdata, Session](ConverterAttemptMock(), 2)

    with pytest.raises(AccountBannedException):
        converter.convert(Tdata("acc/tdata"))
