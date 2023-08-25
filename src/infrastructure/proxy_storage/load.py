import json
from src.domain.entities import Proxy

class JsonProxyLoader:
    def __init__(self, filename: str):
        self._filename = filename

    def load(self) -> Proxy:
        with open(self._filename, 'r', encoding='utf-8') as out:
            return Proxy(**json.load(out))
