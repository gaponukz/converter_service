import auth
import typing
import logging
import flask_cors

from flask import Flask
from flask import request
from flask import send_file

from logic.interfaces import IConverterService
from logic.services import FromSessionToTdataService
from logic.services import FromTdataToSessionService
from logic.converters import FromSessionToTdataConverter
from logic.converters import FromTdataToSessionConverter

server = Flask(__name__)
flask_cors.CORS(server)
server.config['CORS_HEADERS'] = 'Content-Type,uuid,rompegram_key'

logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)

@server.post('/convert')
@auth.auth_required
def convert_action_page():
    convert_from: typing.Literal["SESSION", "TDATA"] = request.form['selected_convert_from']

    if convert_from == "SESSION":
        service_cls = FromSessionToTdataService
        converter_cls = FromSessionToTdataConverter
    
    elif convert_from == "TDATA":
        service_cls = FromTdataToSessionService
        converter_cls = FromTdataToSessionConverter

    service: IConverterService = service_cls(request.headers.get('uuid', ''))

    service.save_file_to_convert(request.files.getlist('files[]'))
    service.convert_files(converter_cls())
    session_id = service.get_session_id()

    return send_file(f'results/{session_id}.zip',
        mimetype = 'zip',
        download_name = 'ConvertedAccountsFiles.zip',
        as_attachment = True
    )

if __name__ == '__main__':
    server.run(port=8080, debug=False)
