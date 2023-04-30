import typing

from src.logic.interfaces import IConverter
from src.logic.interfaces import IConverterService

from src.logic.converters import FromSessionToTdataConverter
from src.logic.converters import FromTdataToSessionConverter
from src.logic.services import FromSessionToTdataService
from src.logic.services import FromTdataToSessionService

class DependenciesDict(typing.TypedDict):
    services: dict[typing.Literal["SESSION", "TDATA"], typing.Type[IConverterService]]
    converters: dict[typing.Literal["SESSION", "TDATA"], typing.Type[IConverter]]

container: DependenciesDict = {
    "services": {
        "SESSION": FromSessionToTdataService,
        "TDATA": FromTdataToSessionService
    },
    "converters": {
        "SESSION": FromSessionToTdataConverter,
        "TDATA": FromTdataToSessionConverter
    }
}
