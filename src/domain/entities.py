import typing
import dataclasses

@dataclasses.dataclass
class Session:
    json_path: str
    session_path: str

@dataclasses.dataclass
class Tdata:
    path: str

@dataclasses.dataclass
class Proxy:
    type: typing.Literal['http', 'https', 'socks4', 'socks5']
    ip: str
    port: int | str
    username: str
    password: str
