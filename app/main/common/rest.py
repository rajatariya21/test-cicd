import dataclasses
from dataclasses import dataclass
from threading import Thread

import requests
from flask import jsonify, make_response
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_oauthlib import OAuth1

import app.main.common.constants as constants


class RestAuth:
    def __init__(self, native_object):
        self.native_object = native_object


class AirbyteError(Exception):
    def __init__(
        self, message=None, object=None, reason=None,
            status_code=None):
        self.message = message
        self.object = object
        self.reason = reason
        self.status_code = status_code
        super().__init__(self.message, object)


@dataclass
class DataserviceException(Exception):
    message: str = "data-service exception"
    status_code: int = None

@dataclass
class ConnectionException(Exception):
    def __init__(self,data=None, message=None,status=None):
        self.data = data
        self.message = message
        self.status= status


@dataclass
class IntrospectionException(Exception):
    message: str = "Error happen while introspecting the sample file"
    status_code: int = None

@dataclass
class MongoException(Exception):
    message: str = "Error while creating MongoClient"
    status: str = None

class ConfigException(Exception):
    def __init__(self,data=None, message=None):
        self.data = data
        self.message = message


@dataclass
class Response:
    url: str = None
    method: str = None
    json_obj: dict = None
    content: str = None
    cookies: str = None
    elapsed: float = None
    headers: dict = None
    is_permanent_redirect: bool = False
    is_redirect: bool = False
    status_code: int = None
    reason: str = None
    response_type: str = None
    data: dict = None


@dataclass
class AppResponse:

    status_code: int = 200
    data: object = None
    errors: list = None
    logs: list = None
    response_type: str = "success"


class RestManager:
    AUTH_BASIC = constants.AUTH_BASIC
    AUTH_DIGEST = constants.AUTH_DIGEST
    AUTH_OAUTH1 = constants.AUTH_OAUTH1
    REQUEST_POST = constants.REQUEST_POST
    REQUEST_GET = constants.REQUEST_GET

    @staticmethod
    def rest_response(data, status, status_code):
        resp_obj = {
            "data": data,
            "status": {"result": status, "code": status_code},
        }
        return make_response(jsonify(resp_obj), status_code)

    @staticmethod
    def get_auth(auth_type, *args):
        if auth_type == RestManager.AUTH_DIGEST:
            return RestAuth(native_object=HTTPDigestAuth(*args))
        elif auth_type == RestManager.AUTH_BASIC:
            return RestAuth(native_object=HTTPBasicAuth(*args))
        elif auth_type == RestManager.AUTH_OAUTH1:
            return RestAuth(native_object=OAuth1(*args))

    @staticmethod
    def post(
        url,
        auth: RestAuth = None,
        data: dict = None,
        headers: list = None,
    ):
        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)
        if auth is not None:
            if isinstance(auth, RestAuth):
                auth = auth.native_object
        response = requests.post(url, auth=auth, json=data, headers=headers)
        response = RestManager.postprocess(response, method=RestManager.REQUEST_POST)
        return response

    @staticmethod
    def postprocess(r, method, jsonify_output: bool = True):
        content = r.content
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        response = Response(
            url=r.url,
            method=method,
            json_obj=None,
            content=content,
            cookies=r.cookies,
            elapsed=r.elapsed,
            headers=r.headers,
            is_permanent_redirect=r.is_permanent_redirect,
            is_redirect=r.is_redirect,
            status_code=r.status_code,
            reason=r.reason,
        )
        if jsonify_output:
            if r.text:
                try:
                    response.json = r.json()
                except Exception:
                    pass
        return response

    @staticmethod
    def get(url, auth=None, headers=None, query_dict: dict = None):
        kwargs = {}
        if query_dict is not None:
            kwargs["params"] = query_dict
        if auth is not None:
            if isinstance(auth, RestAuth):
                auth = auth.native_object
        kwargs["auth"] = auth
        kwargs["headers"] = headers
        response = requests.get(url, **kwargs)
        response = RestManager.postprocess(response, method=RestManager.REQUEST_GET)
        return response

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return
