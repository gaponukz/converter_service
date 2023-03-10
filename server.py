from flask import Flask
from flask import request
from flask import jsonify
from flask import send_file
import flask_cors
import random
import os
import auth
import converter

from typing import Literal, Final
from werkzeug.datastructures import FileStorage

server = Flask(__name__)
flask_cors.CORS(server, support_credentials=True)

FROM_SESSION_ALOWANCE: Final = ['.session', '.json']
FROM_TDATA_ALOWANCE: Final = ['.zip']

@server.post('/convert')
@auth.auth_required
def convert_action_page():
    convert_from: Literal["SESSION", "TDATA"] = request.form.get('selected_convert_from')
    files: list[FileStorage] = request.files.getlist('files[]')

    if convert_from == "SESSION":
        archive_id = str(random.randint(0, 10**6)) + request.headers.get('uuid', '')
        os.mkdir(f"sessions/{archive_id}")

        for file in files:
            if any([file.filename.endswith(ext) for ext in FROM_SESSION_ALOWANCE]):
                file.save(f"sessions/{archive_id}/{file.filename}")
        
        converter.from_session(archive_id)

        return send_file(f'results/{archive_id}.zip',
            mimetype = 'zip',
            download_name = 'ConvertedTDATA.zip',
            as_attachment = True
        )
    
    elif convert_from == "TDATA":
        archive_id = str(random.randint(0, 10**6)) + request.headers.get('uuid', '')
        os.mkdir(f"tdatas/{archive_id}")

        for file in files:
            if any([file.filename.endswith(ext) for ext in FROM_TDATA_ALOWANCE]):
                file.save(f"tdatas/{archive_id}/{file.filename}")
        
        converter.from_tdata(archive_id)

        return send_file(f'results/{archive_id}.zip',
            mimetype = 'zip',
            download_name = 'ConvertedSESSIONS.zip',
            as_attachment = True
        )

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    server.run(port=8080, debug=True)
