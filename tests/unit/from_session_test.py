from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.value_objects import SessionId
from src.domain.errors import AccountBannedException
from src.application.usecases.from_session import ConvertFromSessionToTdata

class TdataDataBaseMock:
    def __init__(self):
        self.tdatas = list[Tdata]()

    def save(self, tdata: Tdata):
        self.tdatas.append(tdata)

class SessionDataBaseMock:
    def read_all(self, session: SessionId) -> list[Session]:
        return [
            Session(f"sessions/{session}/acc1.json", f"sessions/{session}/acc1.session"),
            Session(f"sessions/{session}/acc2.json", f"sessions/{session}/acc2.session")
        ]

class FromSessionConverterMock:
    def convert(self, session: Session) -> Tdata:
        return Tdata(session.json_path.replace("sessios/", "tdatas/").replace(".json", "/tdata"))

class FromSessionConverterFailedMock:
    def convert(self, session: Session) -> Tdata:
        raise AccountBannedException(session.json_path)

def test_usecase_without_exceptions():
    session_db = SessionDataBaseMock()
    tdata_db = TdataDataBaseMock()
    converter = FromSessionConverterMock()

    session_id = "123"
    service = ConvertFromSessionToTdata(session_db, tdata_db, converter)

    service.process(session_id)
    
    assert tdata_db.tdatas == [
        Tdata(path=f'sessions/{session_id}/acc1/tdata'),
        Tdata(path=f'sessions/{session_id}/acc2/tdata')
    ]

def test_usecase_with_exceptions():
    session_db = SessionDataBaseMock()
    tdata_db = TdataDataBaseMock()
    converter = FromSessionConverterFailedMock()

    session_id = "123"
    service = ConvertFromSessionToTdata(session_db, tdata_db, converter)

    service.process(session_id)

    assert tdata_db.tdatas == []
