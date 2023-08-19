import typing

from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.value_objects import SessionId
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException

class TdataDataBase(typing.Protocol):
    def read_all(self, session: SessionId) -> list[Tdata]: ...

class FromSessionConverter(typing.Protocol):
    def convert(self, session: Tdata) -> Session: ...

class SessionDataBase(typing.Protocol):
    def save(self, session: Session): ...

class ConvertFromTdataToSession:
    def __init__(
            self,
            session_db: SessionDataBase,
            tdata_db: TdataDataBase,
            convertor: FromSessionConverter
    ):    
        self.session_db = session_db
        self.tdata_db = tdata_db
        self.convertor = convertor

    def process(self, id: SessionId):
        tdatas = self.tdata_db.read_all(id)

        for tdata in tdatas:
            try:
                session = self.convertor.convert(tdata)
            
            except (AccountBannedException, AccountNotFoundException):
                continue

            self.session_db.save(session)