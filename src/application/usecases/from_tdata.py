import typing

from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.value_objects import SessionId
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException

class SessionDataBase(typing.Protocol):
    def read_all(self, session: SessionId) -> list[Session]: ...

class FromTdataConverter(typing.Protocol):
    def convert(self, session: Session) -> Tdata: ...

class TdataDataBase(typing.Protocol):
    def save(self, session: Tdata): ...

class ConvertFromTdataToSession:
    def __init__(
            self,
            session_db: SessionDataBase,
            tdata_db: TdataDataBase,
            convertor: FromTdataConverter
    ):    
        self.session_db = session_db
        self.tdata_db = tdata_db
        self.convertor = convertor

    def process(self, id: SessionId):
        sessions = self.session_db.read_all(id)

        for session in sessions:
            try:
                tdata = self.convertor.convert(session)
            
            except (AccountBannedException, AccountNotFoundException):
                continue

            self.tdata_db.save(tdata)
