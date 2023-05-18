import os
import abc
import random
import logging

from src import utils
from src.logic.interfaces import IConverter
from src.logic.interfaces import IConverterService
from werkzeug.datastructures import FileStorage

logging.basicConfig(
    filename='service.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)


class ConverterServiceTemplate(IConverterService):
    def __init__(self, uuid: str):
        self._session_id = self.generate_session_id(uuid)

    def generate_session_id(self, uuid: str) -> str:
        return str(random.randint(0, 10**6)) + uuid
    
    def get_session_id(self) -> str:
        return self._session_id
    
    @property
    @abc.abstractmethod
    def folder(self) -> str: ... 

    @abc.abstractmethod
    def is_alowed_extension(self, extension: str) -> bool: ...

    def save_file_to_convert(self, files: list[FileStorage]) -> str:
        os.mkdir(f"{self.folder}/{self._session_id}")

        for file in files:
            if self.is_alowed_extension(file.filename):
                file.save(f"{self.folder}/{self._session_id}/{file.filename}")

    def convert_files(self, converter: IConverter):
        converter.convert(f"{self.folder}/{self._session_id}", f"results/{self._session_id}")

        for folder in os.listdir(f"results/{self._session_id}"):
            utils.make_zip_archive(f"results/{self._session_id}{folder}", True)
            
        utils.make_zip_archive(f"results/{self._session_id}")
        utils.remove_folder(f"{self.folder}/{self._session_id}")

class FromSessionToTdataService(ConverterServiceTemplate):
    def __init__(self, uuid: str):
        super().__init__(uuid)
    
    @property
    def folder(self):
        return "sessions"
    
    def is_alowed_extension(self, extension: str) -> bool:
        return any(extension.endswith(ext) for ext in ['.json', '.session'])


class FromTdataToSessionService(ConverterServiceTemplate):
    def __init__(self, uuid: str):
        super().__init__(uuid)
        self.folder = "tdatas"
    
    def is_alowed_extension(self, extension: str) -> bool:
        return extension.endswith('.zip')
