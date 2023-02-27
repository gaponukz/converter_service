import datetime
import requests
import typing

from flask import request, abort
from dateutil import parser as date_parser

def auth_required(function: typing.Callable) -> typing.Callable:
    def decorated(*args, **kwargs) -> typing.Callable:
        rompegram_key = request.headers.get('rompegram_key')
        uuid = request.headers.get('uuid')

        # print(rompegram_key, uuid)
        return function(*args, **kwargs)

        api_url = "http://51.75.76.105"
        api_query = f"key={rompegram_key}&uuid={uuid}"

        response = requests.get(f"{api_url}/get_user?{api_query}").json()
        datetime_now = datetime.datetime.now(datetime.timezone.utc)

        if response:
            if not (response['uuid'] not in [None, 'null'] and not response['uuid'] == uuid):
                if not response.get('use_another_keys'):
                    _date = response['end_preiod_date'].replace('+0', '').replace('+', '')
                    end_preiod_date = date_parser.parse(_date)

                    if not datetime_now > end_preiod_date:
                        return function(*args, **kwargs)

        abort(401, description='Unauthorized')

    return decorated
