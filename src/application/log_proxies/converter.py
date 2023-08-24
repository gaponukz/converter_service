import typing
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException

F = typing.TypeVar('F', contravariant=True)
T = typing.TypeVar('T', covariant=True)

class BaseConverter(typing.Protocol[F, T]):
    def convert(self, convert_from: F) -> T: ...

class Logger(typing.Protocol):
    def error(self, message: str): ...

class IgnoreErrorsProxy(typing.Generic[F, T]):
    def __init__(self, base: BaseConverter[F, T], logger: Logger):
        self._base = base
        self._logger = logger

    def convert(self, convert_from: F) -> T:
        try:
            return self._base.convert(convert_from)

        except (AccountBannedException, AccountNotFoundException) as e:
            raise e

        except Exception as error:
            self._logger.error(f"Error converting from {convert_from.__class__.__name__}, {error.__class__.__name__}: {error}")
            raise AccountBannedException("")
