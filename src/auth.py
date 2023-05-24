from __future__ import annotations

import abc
import datetime
import requests
import functools
import typing

import flask
from flask import request, abort
from dateutil import parser as date_parser

class AuthenticationPair(typing.TypedDict):
    rompegram_key: str | None
    uuid: str | None

class IRequestAuthenticationHandler(abc.ABC):
    def __init__(self, previous_handler: IRequestAuthenticationHandler | None = None):
        self._previous_handler = previous_handler
    
    @abc.abstractmethod
    def __call__(self, request: flask.Request) -> bool: ...

class RequestAuthenticationHandlerTemplate(IRequestAuthenticationHandler):
    @abc.abstractmethod
    def get_authentication_pair(self, request: flask.Request) -> AuthenticationPair: ...

    def _validate_response(self, response, uuid):
        return response and not (response['uuid'] not in [None, 'null'] and response['uuid'] != uuid)

    def __call__(self, request: flask.Request) -> bool:
        authentication_pair = self.get_authentication_pair(request)
        rompegram_key = authentication_pair.get('rompegram_key')
        uuid = authentication_pair.get('uuid')

        if rompegram_key and uuid:
            api_url = "http://51.75.76.105"
            api_query = f"key={rompegram_key}&uuid={uuid}"

            response = requests.get(f"{api_url}/get_user?{api_query}").json()
            datetime_now = datetime.datetime.now(datetime.timezone.utc)

            if self._validate_response(response, uuid) and not response.get('use_another_keys'):
                end_period_date_str = response['end_preiod_date'].replace('+0', '').replace('+', '')
                end_period_date = date_parser.parse(end_period_date_str)

                if datetime_now <= end_period_date:
                    return True

        if self._previous_handler:
            return self._previous_handler(request)

        return False

class HeadersAuthenticationHandler(RequestAuthenticationHandlerTemplate):
    def get_authentication_pair(self, request: flask.Request) -> AuthenticationPair:
        return {
            "rompegram_key": request.headers.get("rompegram_key"),
            "uuid": request.headers.get("uuid")
        }

class CacheAuthenticationDecorator(RequestAuthenticationHandlerTemplate):
    def __init__(self, handler: RequestAuthenticationHandlerTemplate):
        super().__init__(handler)
        self.handler = handler
        self._cache: dict[str, bool] = {}

    def get_authentication_pair(self, request: flask.Request) -> AuthenticationPair:
        return self.handler.get_authentication_pair(request)

    def __call__(self, request: flask.Request) -> bool:
        # TODO: add lifetime for _cache[key]
        cache_key = self._generate_cache_key(request)

        if self._cache.get(cache_key):
            return True
        
        result = self.handler(request)

        self._cache[cache_key] = result

        return result

    def _generate_cache_key(self, request: flask.Request) -> str:
        authentication_pair = self.get_authentication_pair(request)

        return str(authentication_pair.get('rompegram_key')) + str(authentication_pair.get('uuid'))

def auth_required(function: typing.Callable) -> typing.Callable:
    is_authenticated = CacheAuthenticationDecorator(HeadersAuthenticationHandler())

    @functools.wraps(function)
    def decorated(*args, **kwargs) -> typing.Callable:
        if is_authenticated(request):
            return function(*args, **kwargs)

        abort(401, description='Unauthorized')

    return decorated
