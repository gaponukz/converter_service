import typing

from logic.interfaces import IConverter
from logic.interfaces import IConverterService

from logic.converters import FromSessionToTdataConverter
from logic.converters import FromTdataToSessionConverter
from logic.services import FromSessionToTdataService
from logic.services import FromTdataToSessionService

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
