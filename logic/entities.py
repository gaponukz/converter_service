from __future__ import annotations

import json
import typing
import telethon
import pydantic

from werkzeug.datastructures import FileStorage

Roles: typing.TypeAlias = list[str]
AccountStatus = typing.Literal["No limits", "Not connected", "Spam block", "Dead"]

class BaseModel(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = pydantic.Extra.allow

class Proxy(BaseModel):
    ip: str
    port: int
    username: str
    password: str
    type: str = "http"
    status: typing.Literal["live"] | typing.Any = "live"
    
    def get_proxy(self) -> str:
        return f"{self.type.lower()}://{self.username}:{self.password}@{self.ip}:{self.port}"

    @classmethod
    def from_string(cls, string: str, type="http") -> Proxy:
        try:
            ''' ip:port:username:password '''
            return Proxy(
                type=type,
                ip=string.split(':')[0],
                port=int(string.split(':')[1]),
                username=string.split(':')[2],
                password=string.split(':')[3]
            )
        
        except (ValueError, IndexError):
            try:
                ''' type://username:password@ip:port '''
                return Proxy(
                    type=string.split(':')[0],
                    ip=string.split(':')[2].split('@')[-1],
                    port=int(string.split(':')[-1]),
                    username=string.split(':')[1].replace("//", ""),
                    password=string.split(':')[2].split('@')[0]
                )
            
            except Exception as error:
                raise ValueError(f'Unknown proxy type: {string}') from error
    
    @classmethod
    def parse_object(cls, _object) -> Proxy | None:
        if isinstance(_object, dict):
            return Proxy(**_object) if _object else None

        elif isinstance(_object, list):
            if _object and isinstance(_object[0], dict):
                return Proxy(**_object[0])
        
        return None

class ClientWorker(BaseModel):
    phone: str
    account_path: str
    app_id: str
    app_hash: str
    status: AccountStatus = "No limits"
    register_time: int = 0
    avatar: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    roles: Roles = []
    bio: str | None = None
    twoFA: str | None = None
    session_file: str | None = None
    is_busy: bool = False
    spam_date: float | int | None = None
    device: str | None = None
    lang_pack: str | None = None
    system_lang_pack: str | None = None
    sdk: str | None = None
    app_version: str | None = None
    ipv6: bool | None = False
    proxy: Proxy | None = None

    @pydantic.validator("status", always=True, pre=True)
    def validate_status(cls, value, values):
        if value not in typing.get_args(AccountStatus):
            return "No limits"

        return value
    
    @property
    def telegram_client(self) -> telethon.TelegramClient:
        return telethon.TelegramClient(
            f"{self.account_path}.session",
            self.app_id,
            self.app_hash,
            device_model=self.device,
            lang_code=self.lang_pack,
            system_lang_code=self.system_lang_pack,
            system_version=self.sdk,
            app_version=self.app_version,
            use_ipv6 = self.ipv6,
            proxy = (
                self.proxy.type,
                self.proxy.ip,
                self.proxy.port,
                True, # idk why it here and for what
                self.proxy.username,
                self.proxy.password
            ) if self.proxy else None
        )
    
    def save(self):
        with open(f"{self.account_path}.json", 'w', encoding='utf-8') as out:
            json.dump(self.dict(), out, indent=4)

    @classmethod
    def from_json_file(cls, phone: str, folder_path="accounts"):
        account_path = f"{folder_path}/{phone}"

        with open(f"{account_path}.json", 'r', encoding='utf-8') as out:
            account = json.load(out)
            account.pop('account_path', None)
        
        _proxy = account.pop('proxy', None)
        proxy = Proxy.parse_object(_proxy)

        return cls(proxy=proxy, account_path=account_path, **account)
