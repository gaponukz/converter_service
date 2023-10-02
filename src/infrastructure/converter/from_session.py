import os
import asyncio
from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.infrastructure.converter.tutils import TData
from src.infrastructure.converter.tutils import Proxy


class FromSessionConverter:
    def __init__(self, tdatas_path: str, timeout: int = 20):
        self.tdatas_path = tdatas_path
        self.timeout = timeout

        if not os.path.exists(tdatas_path):
            os.makedirs(tdatas_path)

    def convert(self, session: Session) -> Tdata:
        try:
            coroutine = self._helper(session)
            return asyncio.run(asyncio.wait_for(coroutine, self.timeout))

        except asyncio.TimeoutError:
            raise AccountBannedException(session.json_path)

    async def _helper(self, session: Session) -> Tdata:
        phone = session.json_path.replace(".json", "").split("/")[-1]
        path_to_save = f"{self.tdatas_path}/{phone}/tdata"
        tdata = TData(path_to_save)

        await tdata.session_to_tdata(
            proxy=Proxy.from_json_file("proxy.json").get_proxy(), session=session
        )

        return Tdata(path_to_save)
