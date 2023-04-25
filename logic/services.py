import os
import abc
import random
import logging
import shutil

from logic.interfaces import IConverter
from logic.interfaces import IConverterService
from werkzeug.datastructures import FileStorage

logging.basicConfig(
    filename='service.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)


class ConverterServiceTemplate(IConverterService):
    def __init__(self, uuid: str, folder: str):
        self._folder = folder
        self._session_id = self.generate_session_id(uuid)

    def generate_session_id(self, uuid: str) -> str:
        return str(random.randint(0, 10**6)) + uuid
    
    def get_session_id(self) -> str:
        return self._session_id

    @abc.abstractmethod
    def is_alowed_extension(self, extension: str) -> bool: ...

    def save_file_to_convert(self, files: list[FileStorage]) -> str:
        os.mkdir(f"{self._folder}/{self._session_id}")

        for file in files:
            if self.is_alowed_extension(file.filename):
                file.save(f"{self._folder}/{self._session_id}/{file.filename}")

    def convert_files(self, converter: IConverter):
        converter.convert(f"{self._folder}/{self._session_id}", f"result/{self._session_id}")

        try:
            for folder in os.listdir(f"results/{self._session_id}"):
                try:
                    shutil.make_archive(f"results/{self._session_id}{folder}", 'zip', f"results/{self._session_id}{folder}")
            
                except Exception as error:
                    logging.exception(error)
                
            shutil.make_archive(f"results/{self._session_id}", 'zip', f"results/{self._session_id}")

        except Exception as error:
            logging.exception(error)

        try:
            shutil.rmtree(f"{self._folder}/{self._session_id}")

        except Exception as error:
            logging.exception(error)


class FromSessionToTdataService(ConverterServiceTemplate):
    def __init__(self, uuid: str):
        super().__init__(uuid, "sessions")
    
    def is_alowed_extension(self, extension: str) -> bool:
        return any(extension.endswith(ext) for ext in ['.json', '.session'])


class FromTdataToSessionService(ConverterServiceTemplate):
    def __init__(self, uuid: str):
        super().__init__(uuid, "tdatas")
    
    def is_alowed_extension(self, extension: str) -> bool:
        return extension.endswith('.zip')
