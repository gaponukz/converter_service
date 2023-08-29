from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.value_objects import SessionId
from src.domain.errors import AccountBannedException
from src.application.usecases.from_tdata import ConvertFromTdataToSession

class SessionDataBaseMock:
    def __init__(self):
        self.sessions = list[Session]()

    def save(self, id: SessionId, session: Session):
        self.sessions.append(session)

class TdataDataBaseMock:
    def read_all(self, session: SessionId) -> list[Tdata]:
        return [Tdata(f"tdatas/{session}/{i}/tdata") for i in range(10)]

class FromTdataConverterMock:
    def convert(self, tdata: Tdata) -> Session:
        path = tdata.path.replace("tdatas/", "sessios/").replace("/tdata", "/acc")

        return Session(
            json_path=f"{path}.json",
            session_path=f"{path}.session"
        )

class FromTdataConverterFailedMock:
    def convert(self, tdata: Tdata) -> Session:
        raise AccountBannedException(tdata.path)

def test_usecase_without_exceptions():
    session_db = SessionDataBaseMock()
    tdata_db = TdataDataBaseMock()
    converter = FromTdataConverterMock()

    session_id = "123"
    service = ConvertFromTdataToSession(session_db, tdata_db, converter)

    service.process(session_id)

    assert session_db.sessions == [Session(json_path=f'sessios/{session_id}/{i}/acc.json', session_path=f'sessios/{session_id}/{i}/acc.session') for i in range(10)]

def test_usecase_with_exceptions():
    session_db = SessionDataBaseMock()
    tdata_db = TdataDataBaseMock()
    converter = FromTdataConverterFailedMock()

    session_id = "123"
    service = ConvertFromTdataToSession(session_db, tdata_db, converter)

    service.process(session_id)

    assert session_db.sessions == []
