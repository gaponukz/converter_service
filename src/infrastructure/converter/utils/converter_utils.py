import sqlite3
import telethon
import opentele

from src.domain.entities import Session
from src.domain.errors import AccountBannedException
from src.infrastructure.converter.utils import convert_tdata
from src.infrastructure.converter.utils import entities
from src.infrastructure.converter.utils import utils

async def session_to_string(session: Session) -> str:
    client = entities.ClientWorker.from_session(session)
    return telethon.sessions.StringSession.save(client.telegram_client.session)

async def convert_from_string_to_tdata(string_session: str, path_to_save: str):
    client = opentele.tl.TelegramClient(telethon.sessions.StringSession(string_session))
    tdesk = await client.ToTDesktop(flag=opentele.api.UseCurrentSession)

    tdesk.SaveTData(path_to_save)

async def convert_from_tdata_to_session(tdata_path: str, save_path: str) -> str:
    string_sessoins: list[str] = convert_tdata.convert_tdata(tdata_path)

    for str_session in string_sessoins:
        telegram_useragent_kwargs = utils.get_random_client()
        _str_session = telethon.sessions.StringSession(str_session)

        client = telethon.TelegramClient(_str_session, **telegram_useragent_kwargs)

        try:
            await client.connect()
        
        except:
            raise AccountBannedException(tdata_path)
        
        if not await client.is_user_authorized():
            raise AccountBannedException(tdata_path)
        
        async with client:
            info = await client.get_me()

        try:
            client = telethon.TelegramClient(f"{save_path}/{info.phone}.session", **telegram_useragent_kwargs)

        except sqlite3.OperationalError:
            raise AccountBannedException(tdata_path)
    
        utils.setup_client_from_string_session(client, str_session)

        async with client:
            registered = await utils.get_client_creation_timestamp(client)

        account_data = {
            "session_file": info.phone,
            "phone": info.phone,
            "register_time": registered,
            "avatar": None,
            "first_name": info.first_name,
            "last_name": info.last_name,
            "username": info.username,
            "proxy": None,
            "twoFA": None,
            "status": "No limits",
            "is_busy": False
        }

        new_telegram_useragent_kwargs = dict(telegram_useragent_kwargs.copy())
        new_telegram_useragent_kwargs.pop('proxy')
        account_data.update(new_telegram_useragent_kwargs)
        account_data['account_path'] = f"{save_path}/{info.phone}"
        account_data['app_id'] = str(new_telegram_useragent_kwargs["api_id"])
        account_data['app_hash'] = new_telegram_useragent_kwargs["api_hash"]

        account = entities.ClientWorker(**account_data)
        account.save()
    
    return info.phone
