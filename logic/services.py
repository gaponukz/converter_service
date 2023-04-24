import os
import abc
import logging
import shutil

from logic.entities import FileStorage
from logic.interfaces import IConverter
from logic.interfaces import IConverterService

logging.basicConfig(
    filename='converter.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)

class IConverterServiceTemplate(IConverterService):
    def __init__(self, folder: str):
        self._folder = folder
        self._session_id = self.generate_session_id()
        self._alowed_extensions = self.get_alowed_extensions()

    @abc.abstractmethod
    def generate_session_id(self) -> str: ...

    @abc.abstractmethod
    def get_alowed_extensions(self) -> list[str]: ...

    def save_file_to_convert(self, files: list[FileStorage]) -> str:
        os.mkdir(f"{self._folder}/{self._session_id}")

        for file in files:
            if any([file.filename.endswith(ext) for ext in self._alowed_extensions]):
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
