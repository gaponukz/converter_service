import asyncio
from src.domain.entities import Tdata
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.infrastructure.converter.utils import converter_utils

class FromSessionConverter:
    def __init__(self, tdatas_path: str, timeout: int=20):
        self.tdatas_path = tdatas_path
        self.timeout = timeout
    
    def convert(self, session: Session) -> Tdata:
        try:

            coroutine = self._helper(session)
            return asyncio.run(asyncio.wait_for(coroutine, self.timeout))
        
        except asyncio.TimeoutError:
            raise AccountBannedException(session.json_path)

    async def _helper(self, session: Session) -> Tdata:
        phone = session.json_path.replace('.json', '').split('/')[-1]
        path_to_save = f"{self.tdatas_path}/{phone}/tdata"
        
        await converter_utils.convert_from_string_to_tdata(
            await converter_utils.session_to_string(session),
            path_to_save = path_to_save
        )

        return Tdata(path=path_to_save)
