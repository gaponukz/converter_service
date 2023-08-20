from src.infrastructure.db.session import SessionStorage
from src.infrastructure.db.tdata import TdataStorage
from src.infrastructure.converter.from_session import FromSessionConverter
from src.infrastructure.converter.from_tdata import FromTdataConverter
from src.application.usecases.from_session import ConvertFromSessionToTdata
from src.application.usecases.from_tdata import ConvertFromTdataToSession
from src.application.decorators.before_tdata_onvert import PrepareFilesBeforeConvertDecorator
from src.application.decorators.after_convert import MakeZipAfterConvertDecorator
from src.infrastructure.handler.convert import Controller

import flask_cors
from flask import Flask

app = Flask(__name__)
flask_cors.CORS(app)

session_db = SessionStorage("sessions")
tdata_db = TdataStorage("tdatas")
from_session_converter = FromSessionConverter("tdatas_results")
from_tdata_converter = FromTdataConverter("sessions_results")
from_session_usecase = ConvertFromSessionToTdata(session_db, tdata_db, from_session_converter)
from_session_usecase = MakeZipAfterConvertDecorator(from_session_usecase, "sessions")
from_tdata_usecase = ConvertFromTdataToSession(session_db, tdata_db, from_tdata_converter)
from_tdata_usecase = PrepareFilesBeforeConvertDecorator(from_tdata_usecase, tdata_db, "input")
from_tdata_usecase = MakeZipAfterConvertDecorator(from_tdata_usecase, "tdatas")

controller = Controller(from_tdata_usecase, from_session_usecase)
app.register_blueprint(controller)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
