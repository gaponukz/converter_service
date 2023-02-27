import telethon
import opentele
import random
import asyncio
import datetime
import struct
import base64
import ipaddress
import json

from . import convert_tdata

def TelegramClient(account: str, path="accounts") -> telethon.TelegramClient:
    with open(f"{path}/{account}.json", 'r', encoding='utf-8') as out:
        s_account = json.load(out)
        
    try: proxy = s_account['proxy'][0]
    except: proxy = None

    return telethon.TelegramClient(
        f"{path}/{account}.session",
        s_account['app_id'],
        s_account['app_hash'],
        device_model=s_account.get('device'),
        lang_code=s_account.get('lang_pack'),
        system_lang_code=s_account.get('system_lang_pack'),
        system_version=s_account.get('sdk'),
        app_version=s_account.get('app_version'),
        use_ipv6 = s_account.get('ipv6', False),
        connection_retries = 2,
        proxy = (
            proxy['type'].lower(),
            proxy['ip'],
            int(proxy['port']),
            True, # idk why it here and for what
            proxy['username'],
            proxy['password']
        ) if proxy else None
    )

async def get_client_string_session(account: str, path="accounts") -> str:
    client = TelegramClient(account, path)
    return telethon.sessions.StringSession.save(client.session)

async def convert_from_string_to_tdata(string_session: str, path_to_save: str):
    client = opentele.tl.TelegramClient(telethon.sessions.StringSession(string_session))
    tdesk = await client.ToTDesktop(flag=opentele.api.UseCurrentSession)

    tdesk.SaveTData(path_to_save)

async def convert_from_tdata_to_session(tdata_path: str, save_path: str) -> str:
    string_sessoins: list[str] = convert_tdata.convert_tdata(tdata_path)

    with open("telegram_useragents.json", "r", encoding="utf-8") as out:
        telegram_useragents = json.load(out)

    for str_session in string_sessoins:
        device = random.choice(list(telegram_useragents.keys()))
        api_agent = random.choice(telegram_useragents[device])
        
        telegram_useragent = {
            "app_id": api_agent['app_id'],
            "app_hash": api_agent['app_hash'],
            "sdk": random.choice(telegram_useragents[device])['sdk'],
            "app_version": random.choice(telegram_useragents[device])['app_version'],
            "device": random.choice(telegram_useragents[device])['device'],
            "lang_pack": random.choice(telegram_useragents[device])['lang_pack'],
            "system_lang_pack": random.choice(telegram_useragents[device])['system_lang_pack'],
        }

        _str_session = telethon.sessions.StringSession(str_session)
        client = telethon.TelegramClient(_str_session, api_hash=telegram_useragent["app_hash"],api_id=telegram_useragent["app_id"])

        await client.connect()

        if not await client.is_user_authorized():
            return
        
        async with client:
            info = await client.get_me()

        '''
        "type": "HTTP",
        "ip": "isp2.hydraproxy.com",
        "port": "9989",
        "username": "netw21534ksjh51138",
        "password": "RcpyHHxz3pIM8Ec1_country-Russia",
        '''

        client = telethon.TelegramClient(
            f"{save_path}/{info.phone}.session",
            api_hash=telegram_useragent["app_hash"],
            api_id=telegram_useragent["app_id"],
            device_model=telegram_useragent['device'],
            lang_code=telegram_useragent.get('lang_pack'),
            system_lang_code=telegram_useragent.get('system_lang_pack'),
            system_version=telegram_useragent.get('sdk'),
            app_version=telegram_useragent.get('app_version'),
            use_ipv6 = telegram_useragent.get('ipv6', False),
            connection_retries = 2,
            proxy = ("http", "isp2.hydraproxy.com", 9989, True, "netw21534ksjh51138", "RcpyHHxz3pIM8Ec1_country-Russia")
        )

        dc, ip_bytes, port, key = struct.unpack(">B4sH256s", base64.urlsafe_b64decode(str_session[1:].encode("ascii")))

        client.session.set_dc(dc, str(ipaddress.ip_address(ip_bytes)), port)
        client.session.auth_key = telethon.crypto.authkey.AuthKey(key) # ?
        client.session.save()
        
        client._sender = telethon.network.mtprotosender.MTProtoSender(
            telethon.crypto.authkey.AuthKey(key),
            loggers=client._log,
            retries=client._connection_retries,
            delay=client._retry_delay,
            auto_reconnect=client._auto_reconnect,
            connect_timeout=client._timeout,
            auth_key_callback=client._auth_key_callback,
            update_callback=client._handle_update,
            auto_reconnect_callback=client._handle_auto_reconnect
        )

        async with client:
            await client.send_message("@creationdatebot", "/start")
            await asyncio.sleep(0.5)

            message = (await client.get_messages("@creationdatebot"))[0].message
            registered = datetime.datetime.strptime(message.split(" registered: ")[-1].split()[0], '%Y-%m-%d')
            registered = datetime.datetime.timestamp(registered)

            with open(f"{save_path}/{info.phone}.json", "w", encoding="utf-8") as out:
                json.dump({
                    "session_file": info.phone,
                    "phone": info.phone,
                    "register_time": registered,
                    "app_id": telegram_useragent['app_id'],
                    "app_hash": telegram_useragent['app_hash'],
                    "sdk": telegram_useragent['sdk'],
                    "app_version": telegram_useragent['app_version'],
                    "device": telegram_useragent['device'],
                    "avatar": None,
                    "first_name": info.first_name,
                    "last_name": info.last_name,
                    "username": info.username,
                    "lang_pack": telegram_useragent['lang_pack'],
                    "system_lang_pack": telegram_useragent['system_lang_pack'],
                    "proxy": None,
                    "twoFA": None,
                    "ipv6": False,
                    "status": "No limits",
                    "is_busy": False
                }, out, indent=4)
    
    return info.phone
