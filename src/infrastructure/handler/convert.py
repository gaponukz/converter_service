import os
import uuid
import typing

from flask import Blueprint
from flask import request
from flask import send_file
from flask import Response

from src.domain.value_objects import SessionId


class ConverterService(typing.Protocol):
    def process(self, id: SessionId):
        ...


class ProxyChecker(typing.Protocol):
    def is_alive(self) -> bool:
        ...


class Controller(Blueprint):
    def __init__(
        self,
        from_tdata: ConverterService,
        from_session: ConverterService,
        checker: ProxyChecker,
    ):
        self.from_tdata = from_tdata
        self.from_session = from_session
        self.checker = checker

        super().__init__("controller", __name__)
        self.convert_action_page = self.post("/convert")(self._convert_action_page)
        self.is_proxy_alive_page = self.get("/is_alive")(self._is_proxy_alive_page)

    def _convert_action_page(self):
        session = str(uuid.uuid4())
        convert_from: typing.Literal["SESSION", "TDATA"] = request.form[
            "selected_convert_from"
        ]

        os.mkdir(f"input/{session}")

        for file in request.files.getlist("files[]"):
            file.save(f"input/{session}/{file.filename}")

        if convert_from == "SESSION":
            self.from_session.process(session)

        elif convert_from == "TDATA":
            self.from_tdata.process(session)

        return send_file(
            f"results/{session}.zip",
            mimetype="zip",
            download_name="ConvertedAccountsFiles.zip",
            as_attachment=True,
        )

    def _is_proxy_alive_page(self):
        if self.checker.is_alive():
            return Response("alive", status=200)

        else:
            return Response("not alive", status=500)
