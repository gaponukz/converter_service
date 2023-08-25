from src.domain.entities import Tdata
from src.domain.entities import Session
from src.infrastructure.db.session import SessionStorage
from src.infrastructure.db.tdata import TdataStorage
from src.infrastructure.converter.from_session import FromSessionConverter
from src.infrastructure.converter.from_tdata import FromTdataConverter
from src.application.usecases.from_session import ConvertFromSessionToTdata
from src.application.usecases.from_tdata import ConvertFromTdataToSession
from src.application.usecases.proxy_checker import ProxyChecker
from src.application.decorators.before_tdata_onvert import PrepareFilesBeforeConvertDecorator
from src.application.decorators.after_convert import MakeZipAfterConvertDecorator
from src.application.log_proxies.converter import IgnoreErrorsProxy
from src.infrastructure.handler.convert import Controller
from src.infrastructure.logger.console import ConsoleLogger
from src.infrastructure.proxy_storage.load import JsonProxyLoader
import flask_cors
from flask import Flask

app = Flask(__name__)
flask_cors.CORS(app)

logger = ConsoleLogger()
tdata_db = TdataStorage("tdatas")
from_session_converter = IgnoreErrorsProxy[Session, Tdata](FromSessionConverter("tdatas_results"), logger)
from_tdata_converter = IgnoreErrorsProxy[Tdata, Session](FromTdataConverter("sessions_results"), logger)
from_session_usecase = ConvertFromSessionToTdata(SessionStorage("input"), tdata_db, from_session_converter)
from_session_usecase = MakeZipAfterConvertDecorator(from_session_usecase, "tdatas")
from_tdata_usecase = ConvertFromTdataToSession(SessionStorage("sessions"), TdataStorage("tdatas"), from_tdata_converter)
from_tdata_usecase = PrepareFilesBeforeConvertDecorator(from_tdata_usecase, tdata_db, "input")
from_tdata_usecase = MakeZipAfterConvertDecorator(from_tdata_usecase, "sessions")
proxy_checker_usecase = ProxyChecker(JsonProxyLoader("proxy.json").load())

controller = Controller(from_tdata_usecase, from_session_usecase, proxy_checker_usecase)
app.register_blueprint(controller)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)
