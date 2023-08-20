import os
import typing

from flask import Blueprint
from flask import request

from src.domain.value_objects import SessionId

class ConverterService(typing.Protocol):
    def process(self, id: SessionId): ...

class Controller(Blueprint):
    def __init__(self, from_tdata: ConverterService, from_session: ConverterService):
        self.from_tdata = from_tdata
        self.from_session = from_session

        super().__init__('controller', __name__)
        self.convert_action_page = self.post('/convert')(self._convert_action_page)
    
    def _convert_action_page(self):
        session = "123"
        convert_from: typing.Literal["SESSION", "TDATA"] = request.form['selected_convert_from']

        os.mkdir(f"input/{session}")
        
        for file in request.files.getlist('files[]'):
            file.save(f"input/{session}/{file.filename}")
        
        if convert_from == "SESSION":
            self.from_session.process(session)
        
        elif convert_from == "TDATA":
            self.from_tdata.process(session)

        return ""
