import asyncio
from src.domain.entities import Tdata
from src.domain.entities import Session
from src.infrastructure.converter.utils import converter_utils

class FromTdataConverter:
    def __init__(self, sessions_path: str, timeout: int=20):
        self.sessions_path = sessions_path
        self.timeout = timeout
    
    def convert(self, tdata: Tdata) -> Session:
        phone = asyncio.run(asyncio.wait_for(
            converter_utils.convert_from_tdata_to_session(
                tdata.path,
                self.sessions_path
            ), self.timeout
        ))

        return Session(
            json_path=f"{self.sessions_path}/{phone}.json",
            session_path=f"{self.sessions_path}/{phone}.session"
        )
