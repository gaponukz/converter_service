import os
import asyncio
from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.infrastructure.converter.tutils import convert_from_tdata_to_session


class FromTdataConverter:
    def __init__(self, sessions_path: str, timeout: int = 20):
        self.sessions_path = sessions_path
        self.timeout = timeout

        if not os.path.exists(sessions_path):
            os.makedirs(sessions_path)

    def convert(self, tdata: Tdata) -> Session:
        try:
            coroutine = convert_from_tdata_to_session(tdata.path, self.sessions_path)
            phone = asyncio.run(asyncio.wait_for(coroutine, self.timeout))

        except asyncio.TimeoutError:
            raise AccountBannedException(tdata.path)

        return Session(
            json_path=f"{self.sessions_path}/{phone}.json",
            session_path=f"{self.sessions_path}/{phone}.session",
        )
