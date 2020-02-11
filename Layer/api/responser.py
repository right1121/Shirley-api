import json
from http import HTTPStatus


class responser():
    __headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
        }

    def __init__(self):
        self.__status_code = HTTPStatus.OK
        self.__headers = responser.__headers
        self.__body = {}

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, _status_code):
        self.__status_code = _status_code

    @property
    def header(self):
        return self.__headers

    @header.setter
    def header(self, _headers):
        self.__headers = _headers

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, _body):
        self.__body = _body

    def format(self):
        return {
            'statusCode': self.__status_code,
            'headers': self.__headers,
            'body': json.dumps(self.__body)
        }

    @classmethod
    def validation_error(cls, body=None):
        if body is None:
            body = {}
        elif type(body) is not dict:
            raise TypeError

        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'headers': responser.__headers,
            'body': json.dumps(body)
        }

    @classmethod
    def exception_error(cls, body=None):
        if body is None:
            body = {}
        elif type(body) is not dict:
            raise TypeError

        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': responser.__headers,
            'body': json.dumps(body)
        }
