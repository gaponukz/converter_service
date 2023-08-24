import typing
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException

F = typing.TypeVar('F', contravariant=True)
T = typing.TypeVar('T', covariant=True)

class BaseConverter(typing.Protocol[F, T]):
    def convert(self, convert_from: F) -> T: ...

class IgnoreErrorsProxy(typing.Generic[F, T]):
    def __init__(self, base: BaseConverter[F, T]):
        self._base = base

    def convert(self, convert_from: F) -> T:
        try:
            return self._base.convert(convert_from)

        except (AccountBannedException, AccountNotFoundException) as e:
            raise e

        except Exception as error:
            print(f"Error converting from {convert_from.__class__.__name__}, {error.__class__.__name__}: {error}")
            raise AccountBannedException("")
