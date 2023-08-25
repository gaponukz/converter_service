import os
import typing
import shutil

from src.domain.entities import Tdata
from src.domain.value_objects import SessionId

class Service(typing.Protocol):
    def process(self, id: SessionId): ...

class MakeZipAfterConvertDecorator:
    def __init__(self, service: Service, directory: str):
        self.service = service
        self.directory = directory
    
    def process(self, id: SessionId):
        self.service.process(id)

        shutil.make_archive(f"{self.directory}/{id}", 'zip', f"{self.directory}/{id}")
        shutil.copy(f"{self.directory}/{id}.zip", f"results/{id}.zip")
        shutil.rmtree(f"{self.directory}/{id}")
