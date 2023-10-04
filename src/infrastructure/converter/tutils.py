from __future__ import annotations

import os
import typing
import asyncio
import sqlite3
import datetime
import shutil
import json
import pydantic
from opentele.api import UseCurrentSession, APIData
from opentele.tl import TelegramClient as TC
from opentele.td import TDesktop as TD
from src.domain.entities import Session
from src.domain.errors import AccountBannedException
import random


def get_random_attr() -> dict:
    with sqlite3.connect("accounts_info.db") as sqlite_connection:
        cursor = sqlite_connection.cursor()

        sqlite_selection_query = "SELECT * FROM REGISTRATOR;"
        cursor.execute(sqlite_selection_query)
        record = cursor.fetchall()
        record = random.choice(record)
        cursor.close()

        return dict(
            zip(
                [
                    "app_id",
                    "app_hash",
                    "sdk",
                    "device",
                    "app_version",
                    "lang_pack",
                    "system_lang_pack",
                ],
                record,
            )
        )


def get_json(session_phone: str, attrs: dict, session_dir):
    register_time = int(datetime.datetime.now().timestamp())

    jsonic = {
        "session_file": session_phone,
        "phone": session_phone,
        "register_time": register_time,
        "app_id": attrs["app_id"],
        "app_hash": attrs["app_hash"],
        "sdk": attrs["sdk"],
        "app_version": attrs["app_version"],
        "device": attrs["device"],
        "last_check_time": register_time,
        "first_name": "",
        "last_name": "",
        "username": "",
        "sex": 0,
        "lang_pack": attrs["lang_pack"],
        "system_lang_pack": attrs["system_lang_pack"],
        "ipv6": False,
    }
    return json.dump(jsonic, open(f"{session_dir}/{session_phone}.json", "w+"))


async def convert_from_tdata_to_session(tdata_path: str, session_path: str) -> str:
    rand_attrs = get_random_attr()
    api_data = APIData(
        api_id=rand_attrs["app_id"],
        api_hash=rand_attrs["app_hash"],
        device_model=rand_attrs["device"],
        system_version=rand_attrs["sdk"],
        app_version=rand_attrs["app_version"],
        system_lang_code=rand_attrs["system_lang_pack"],
        lang_pack=rand_attrs["lang_pack"],
    )
    session_id = random.randrange(100, 999)
    tdesk = TD(tdata_path, api=api_data)
    if not tdesk.isLoaded():
        raise AccountBannedException(tdata_path)

    session = await asyncio.wait_for(
        tdesk.ToTelethon(
            session=f"{session_path}/{session_id}.session",
            flag=UseCurrentSession,
            proxy=Proxy.from_json_file("proxy.json").to_tuple(),
        ),
        5,
    )

    try:
        await asyncio.sleep(3)
        await asyncio.wait_for(session.connect(), 5)
    except:
        await asyncio.wait_for(session.disconnect(), 1)
        raise AccountBannedException(tdata_path)

    data = await asyncio.wait_for(session.get_me(), 1)

    if data is None:
        await asyncio.wait_for(session.disconnect(), 1)
        raise AccountBannedException(tdata_path)

    phone = data.phone
    get_json(phone, rand_attrs, session_path)
    await asyncio.wait_for(session.disconnect(), 1)

    os.rename(f"{session_path}/{session_id}.session", f"{session_path}/{phone}.session")

    return data.phone


class TData:
    def __init__(self, path_to_save: str):
        self.path_to_save = path_to_save

    async def session_to_tdata(self, proxy: TupleProxy, session: Session) -> None:
        rand_attrs = get_random_attr()
        session_path = session.session_path
        api_data = APIData(
            api_id=rand_attrs["app_id"],
            api_hash=rand_attrs["app_hash"],
            device_model=rand_attrs["device"],
            system_version=rand_attrs["sdk"],
            app_version=rand_attrs["app_version"],
            system_lang_code=rand_attrs["system_lang_pack"],
            lang_pack=rand_attrs["lang_pack"],
        )
        client = TC(session_path, api=api_data, proxy=proxy)
        tdesk = await client.ToTDesktop(flag=UseCurrentSession)

        try:
            tdesk.SaveTData(self.path_to_save)
            print(session_path[0:-8])
        except TypeError:
            print(session_path[0:-8])
            pass

        await client.disconnect()

    def pack_to_zip(self, tdata_path: str) -> None:
        shutil.make_archive(f"{tdata_path}", "zip", tdata_path)


class BaseModel(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = pydantic.Extra.allow


TupleProxy: typing.TypeAlias = tuple[str, str, int, bool, str, str]


class Proxy(BaseModel):
    ip: str
    port: int
    username: str
    password: str
    type: str = "http"
    status: str = "live"

    def get_proxy(self) -> str:
        return f"{self.type.lower()}://{self.username}:{self.password}@{self.ip}:{self.port}"

    def to_tuple(self) -> TupleProxy:
        return (self.type, self.ip, self.port, True, self.username, self.password)

    @classmethod
    def from_string(cls, string: str, type="http") -> Proxy:
        try:
            """ip:port:username:password"""
            return Proxy(
                type=type,
                ip=string.split(":")[0],
                port=int(string.split(":")[1]),
                username=string.split(":")[2],
                password=string.split(":")[3],
            )

        except (ValueError, IndexError):
            try:
                """type://username:password@ip:port"""
                return Proxy(
                    type=string.split(":")[0],
                    ip=string.split(":")[2].split("@")[-1],
                    port=int(string.split(":")[-1]),
                    username=string.split(":")[1].replace("//", ""),
                    password=string.split(":")[2].split("@")[0],
                )

            except Exception as error:
                raise ValueError(f"Unknown proxy type: {string}") from error

    @classmethod
    def from_json_file(cls, filename: str) -> Proxy:
        with open(filename, "r", encoding="utf-8") as out:
            return Proxy(**json.load(out))

    @classmethod
    def parse_object(cls, _object) -> Proxy | None:
        if isinstance(_object, dict):
            return Proxy(**_object) if _object else None

        elif isinstance(_object, list):
            if _object and isinstance(_object[0], dict):
                return Proxy(**_object[0])

        return None
