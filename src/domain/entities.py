import dataclasses

@dataclasses.dataclass
class Session:
    json_path: str
    session_path: str

@dataclasses.dataclass
class Tdata:
    path: str
