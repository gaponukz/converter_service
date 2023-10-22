import os
import shutil
from src.domain.entities import Session, Tdata
from src.domain.value_objects import SessionId


class SessionStorage:
    def __init__(self, directory: str):
        self.directory = directory
        self._failed_dir = "failed"

        if not os.path.exists(directory):
            os.makedirs(directory)

    def save(self, id: SessionId, session: Session):
        json_filename = os.path.basename(session.json_path)
        session_filename = os.path.basename(session.session_path)

        parent_dir = os.path.basename(os.path.dirname(session.json_path))
        new_parent_dir = os.path.join(self.directory, id, parent_dir)

        os.makedirs(new_parent_dir, exist_ok=True)

        new_json_path = os.path.normpath(os.path.join(new_parent_dir, json_filename))
        new_session_path = os.path.normpath(
            os.path.join(new_parent_dir, session_filename)
        )

        shutil.move(session.json_path, new_json_path)
        shutil.move(session.session_path, new_session_path)

    def save_as_failed(self, id: SessionId, tdata: Tdata):
        acc = os.path.split(tdata.path)[-2]
        path_to_failed = os.path.join(self.directory, id, self._failed_dir)

        if not os.path.exists(path_to_failed):
            os.makedirs(path_to_failed, exist_ok=True)

        shutil.move(tdata.path, os.path.join(path_to_failed, f"{acc}/tdata"))

    def read_all(self, session: SessionId) -> list[Session]:
        sessions = set[str]()

        for filename in os.listdir(f"{self.directory}/{session}"):
            if filename.endswith(".json"):
                sessions.add(f"{self.directory}/{session}/{filename}")

        return [
            Session(json_path=path, session_path=path.replace(".json", ".session"))
            for path in sessions
        ]
