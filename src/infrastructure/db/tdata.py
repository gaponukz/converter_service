import os
import shutil
from src.domain.entities import Tdata, Session
from src.domain.value_objects import SessionId


class TdataStorage:
    def __init__(self, directory: str):
        self.directory = directory
        self._failed_dir = "failed"

        if not os.path.exists(directory):
            os.makedirs(directory)

    def save(self, id: SessionId, tdata: Tdata):
        parent_dirs = os.path.dirname(os.path.relpath(tdata.path))
        parent_dirs_list = [id] + parent_dirs.split(os.path.sep)[1:]
        new_parent_dirs = os.path.join(self.directory, *parent_dirs_list)

        os.makedirs(new_parent_dirs)

        new_tdata_path = os.path.join(new_parent_dirs, os.path.basename(tdata.path))

        shutil.move(tdata.path, new_tdata_path)

    def save_as_failed(self, id: SessionId, session: Session):
        acc = os.path.split(session.session_path)[-1].removesuffix(".session")
        path_to_failed = os.path.join(self.directory, id, self._failed_dir)

        if not os.path.exists(path_to_failed):
            os.makedirs(path_to_failed, exist_ok=True)

        shutil.move(session.json_path, os.path.join(path_to_failed, f"{acc}.json"))
        shutil.move(
            session.session_path, os.path.join(path_to_failed, f"{acc}.session")
        )

    def read_all(self, session: SessionId) -> list[Tdata]:
        tdatas = []

        for filename in os.listdir(f"{self.directory}/{session}"):
            if os.path.exists(f"{self.directory}/{session}/{filename}/tdata"):
                tdatas.append(
                    Tdata(path=f"{self.directory}/{session}/{filename}/tdata")
                )

        return tdatas
