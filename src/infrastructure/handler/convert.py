import typing
# import flask_cors

from flask import Flask
from flask import request
from flask import send_file


server = Flask(__name__)

@server.post('/convert')
def convert_action_page():
    session = "123"
    convert_from: typing.Literal["SESSION", "TDATA"] = request.form['selected_convert_from']

    for file in request.files.getlist('files[]'):
        file.save(f"garbage/{session}/{file}")

    return ""
