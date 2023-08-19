from src.domain.entities import Tdata
from src.domain.entities import Session
from src.infrastructure.db.tdata import TdataStorage
from src.infrastructure.db.session import SessioStorage
from src.application.usecases.from_tdata import ConvertFromTdataToSession
from src.application.decorators.before_tdata_onvert import PrepareFilesBeforeConvertDecorator

class Conv:
    def convert(self, session: Session) -> Tdata:
        return Tdata('')

session_db = SessioStorage("sessions")
tdata_db = TdataStorage("tdatas")

service = PrepareFilesBeforeConvertDecorator(ConvertFromTdataToSession(
    session_db,
    tdata_db,
    Conv()
), tdata_db, 'garbage')

service.process("123")
