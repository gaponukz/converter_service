import abc

from werkzeug.datastructures import FileStorage

class IConverter(abc.IConverter):
    @abc.abstractmethod
    def convert(self, input_folder: str, output_folder: str): ...

class IConverterService(abc.ABC):
    @abc.abstractmethod
    def get_session_id(self) -> str: ...
    
    @abc.abstractmethod
    def save_file_to_convert(self, files: list[FileStorage]) -> str: ...

    @abc.abstractmethod
    def convert_files(self, converter: IConverter): ...
