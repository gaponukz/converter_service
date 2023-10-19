import typing
from src.domain.errors import AccountNotFoundException

F = typing.TypeVar("F", contravariant=True)
T = typing.TypeVar("T", covariant=True)


class BaseConverter(typing.Protocol[F, T]):
    def convert(self, convert_from: F) -> T:
        ...


class ConvertAttemptDecorator(typing.Generic[F, T]):
    def __init__(self, base: BaseConverter[F, T], attempt: int):
        self._base = base
        self._attempt = attempt

    def convert(self, convert_from: F) -> T:
        last_error: Exception | None = None

        for _ in range(self._attempt):
            try:
                return self._base.convert(convert_from)

            except AccountNotFoundException as error:
                raise error

            except Exception as error:
                last_error = error

        if last_error is not None:
            raise error
