import math
import typing
import threading
from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.value_objects import SessionId
from src.domain.errors import AccountBannedException
from src.domain.errors import AccountNotFoundException

class SessionDataBase(typing.Protocol):
    def read_all(self, session: SessionId) -> list[Session]: ...

class FromSessionConverter(typing.Protocol):
    def convert(self, session: Session) -> Tdata: ...

class TdataDataBase(typing.Protocol):
    def save(self, session: SessionId, tdata: Tdata): ...


class ConvertFromSessionToTdata:
    def __init__(
            self,
            session_db: SessionDataBase,
            tdata_db: TdataDataBase,
            convertor: FromSessionConverter,
            thread_limit: int = 5
    ):    
        self.session_db = session_db
        self.tdata_db = tdata_db
        self.convertor = convertor
        self.thread_limit = thread_limit

    def process(self, id: SessionId):
        sessions = self.session_db.read_all(id)
        threads = [threading.Thread(target=self._convert_account, args=(id, session)) for session in sessions]

        for group in self._devide_list(threads):
            for thread in group:
                thread.start()

            for thread in group:
                thread.join()

    def _convert_account(self, id: SessionId, session: Session):
            try:
                tdata = self.convertor.convert(session)
            
            except (AccountBannedException, AccountNotFoundException):
                return

            self.tdata_db.save(id, tdata)

    def _devide_list(self, array: list[threading.Thread]) -> list[list[threading.Thread]]:
        div_number = math.ceil(len(array) / self.thread_limit)
        result: list[list] = []
        start_index = 0

        for index in range(1, div_number+1):
            result.append(array[start_index:index*self.thread_limit])

            start_index = index * self.thread_limit
        
        return result
