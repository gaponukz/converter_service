import abc

from logic.entities import FileStorage

class IConverter(abc.IConverter):
    @abc.abstractmethod
    def convert(self, input_folder: str, output_folder: str): ...

class IConverterService(abc.ABC):
    @abc.abstractmethod
    def save_file_to_convert(self, files: list[FileStorage]) -> str: ...

    @abc.abstractmethod
    def convert_files(self, converter: IConverter): ...
