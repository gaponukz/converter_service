import auth
import typing
import flask_cors

from flask import Flask
from flask import request
from flask import send_file

from dependencies import container
from logic.interfaces import IConverter
from logic.interfaces import IConverterService

server = Flask(__name__)
flask_cors.CORS(server)
server.config['CORS_HEADERS'] = 'Content-Type,uuid,rompegram_key'

@server.post('/convert')
@auth.auth_required
def convert_action_page():
    convert_from: typing.Literal["SESSION", "TDATA"] = request.form['selected_convert_from']
    service: IConverterService = container["services"][convert_from](request.headers.get('uuid', ''))
    converter: IConverter = container["converters"][convert_from]()

    service.save_file_to_convert(request.files.getlist('files[]'))
    service.convert_files(converter)
    session_id = service.get_session_id()

    return send_file(f'results/{session_id}.zip',
        mimetype = 'zip',
        download_name = 'ConvertedAccountsFiles.zip',
        as_attachment = True
    )

if __name__ == '__main__':
    server.run(port=8080, debug=False)
