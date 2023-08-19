import os
import typing
import zipfile
import shutil
import patoolib

from src.domain.entities import Tdata
from src.domain.value_objects import SessionId

class Service(typing.Protocol):
    def process(self, id: SessionId): ...

class TdataDataBase(typing.Protocol):
    def save(self, session: Tdata): ...

class PrepareFilesBeforeConvertDecorator:
    def __init__(self, base: Service, db: TdataDataBase, directory: str):
        self.base = base
        self.db = db
        self.directory = directory
    
    def process(self, id: SessionId):
        for filename in os.listdir(f"{self.directory}/{id}"):
            if not filename.endswith(".zip"):
                continue
        
            extract_nested_zip(
                f"{self.directory}/{id}/{filename}",
                f"{self.directory}/{id}"
            )

        for filename in os.listdir(f"{self.directory}/{id}"):
            self.db.save(Tdata(f"{self.directory}/{id}/{filename.replace('.zip', '')}"))

        self.base.process(id)

def extract_nested_zip(archive_path: str, save_path: str):
    if not is_nested_archive(archive_path):
        unzip_archive(archive_path, save_path)
        remove_file(archive_path)
        return

    with zipfile.ZipFile(archive_path, 'r') as archive:
        for file in archive.filelist:
            if not file.filename.endswith('.zip'):
                continue

            with archive.open(file.filename) as zf, open(f"{save_path}/{file.filename}", 'wb') as out:
                shutil.copyfileobj(zf, out)
            
            extract_nested_zip(f"{save_path}/{file.filename}", save_path)
            _extract_zip(f"{save_path}/{file.filename}")
            remove_file(f"{save_path}/{file.filename}")

def remove_folder(folder_path: str):
    shutil.rmtree(folder_path)

def remove_file(file_path: str):
    os.remove(file_path)

def make_zip_archive(directory_path: str, remove: bool=False):
    if directory_path.endswith('.zip'):
        return
    
    shutil.make_archive(directory_path, 'zip', directory_path)
    
    if remove:
        remove_folder(directory_path)

def unzip_archive(archive, outdir):
    patoolib.extract_archive(archive, 0, outdir)

def is_nested_archive(archive_path: str) -> bool:
    with zipfile.ZipFile(archive_path, 'r') as archive:
        return any(file.filename.endswith('.zip') for file in archive.filelist)

def _extract_zip(archive_path: str):
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(archive_path.removesuffix(".zip"))
