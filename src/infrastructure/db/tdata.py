import os
import shutil
from src.domain.entities import Tdata
from src.domain.value_objects import SessionId


class TdataStorage:
    def __init__(self, directory: str):
        self.directory = directory

        if not os.path.exists(directory):
            os.makedirs(directory)

    def save(self, id: SessionId, tdata: Tdata):
        parent_dirs = os.path.dirname(os.path.relpath(tdata.path))
        parent_dirs_list = list(set(parent_dirs.split(os.path.sep)[1:] + [id]))

        new_parent_dirs = os.path.join(self.directory, *parent_dirs_list)

        os.makedirs(new_parent_dirs, exist_ok=True)

        new_tdata_path = os.path.join(new_parent_dirs, os.path.basename(tdata.path))
        shutil.move(tdata.path, new_tdata_path)

    def read_all(self, session: SessionId) -> list[Tdata]:
        tdatas = []

        for filename in os.listdir(f"{self.directory}/{session}"):
            if os.path.exists(f"{self.directory}/{session}/{filename}/tdata"):
                tdatas.append(
                    Tdata(path=f"{self.directory}/{session}/{filename}/tdata")
                )

        return tdatas
