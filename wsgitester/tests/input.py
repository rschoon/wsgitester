
import json
import requests
import sys

from six.moves.urllib.parse import parse_qsl

from . import *

def parse_content_type(environ):
    content_type = environ.get("CONTENT_TYPE")
    result = content_type.split("; ")
    if len(result) == 1:
        return result[0], None
    else:
        return tuple(result)

#
# Basic Post Tests
#

class PostTestBase(Test):
    abstract = True

    def data(self):
        return [
            ('pie', 'apple'),
            ('cake', 'chocolate'),
            ('ice cream', 'vanilla')
        ]

    def err(self, start_response, msg):
        start_response('200 OK', [('Content-type', 'application/json')])
        return [json.dumps({'err': msg}).encode('utf-8')]

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.headers['content-type'] != "application/json":
            return TestFail("Got content type %r instead of application/json" %
                            (resp.headers['content-type'], ))

        try:
            data = json.loads(resp.text)
        except ValueError:
            return TestFail("Couldn't parse result data.")

        if 'err' in data:
            return TestFail(data['err'])

        expected = self.data()
        got = [(k, v) for k, v in data.get("data")]

        expected_extra = []
        for item in expected:
            if item in got:
                got.remove(item)
            else:
                expected_extra.append(item)

        if len(expected_extra) > 0:
            return TestFail("Missing items: %r" % expected)

        if len(got) > 0:
            return TestFail("Got extra items: %r" % got)

        return TestPass()

class QueryTest(PostTestBase):
    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-type', 'application/json')])

        q = parse_qsl(environ.get("QUERY_STRING", ""))
        return [json.dumps({'data': q}).encode('utf-8')]

    def make_request(self, url):
        return requests.get(url, params=self.data())

class PostExactReadTest(PostTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            content_length = int(environ.get("CONTENT_LENGTH", 0))
            data = environ['wsgi.input'].read(content_length)

            start_response('200 OK', [('Content-type', 'application/json')])
            q = parse_qsl(data.decode('utf-8'))
            return [json.dumps({'data': q}).encode('utf-8')]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

class PostChunkyReadTest(PostTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = []
            remaining = int(environ.get("CONTENT_LENGTH", 0))
            while remaining > 0:
                s = environ['wsgi.input'].read(min(remaining, 8))
                if s == "":
                    return self.err(start_response,
                                    "premature EOF")
                data.append(s)
                remaining -= len(s)

            start_response('200 OK', [('Content-type', 'application/json')])

            data = (b"".join(data)).decode(encoding='utf8')
            q = parse_qsl(data)
            return [json.dumps({'data': q}).encode('utf-8')]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

class PostLineTest(PostTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = environ['wsgi.input'].readline()

            start_response('200 OK', [('Content-type', 'application/json')])

            data = data.decode(encoding='utf8')
            q = parse_qsl(data)
            return [json.dumps({'data': q}).encode('utf-8')]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

class PostTest(PostTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = environ['wsgi.input'].read()

            start_response('200 OK', [('Content-type', 'application/json')])

            data = data.decode(encoding='utf8')
            q = parse_qsl(data)
            return [json.dumps({'data': q}).encode('utf-8')]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

#
# Nul Byte Post Tests
#

class PostNulTestBase(Test):
    abstract = True

    def data(self):
        return b'\0pie\0cake\0'

    def expected_data(self):
        return self.data()

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.headers['content-type'] == "application/json":
            try:
                data = json.loads(resp.text)
            except ValueError:
                return TestFail("Couldn't parse result data.")

            if 'err' in data:
                return TestFail(data['err'])
            return TestFail("Got application/json for a non-error")

        if resp.headers['content-type'] != "application/octet-stream":
            return TestFail("Didn't get expected content type.")

        if resp.content != self.expected_data():
            return TestFail("Didn't get expected content (%d bytes)" %
                            len(resp.content))

class PostNulTest(PostNulTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = environ['wsgi.input'].read()

            start_response("200 OK", [
                ("Content-Type", "application/octet-stream")
            ])
            return [data]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

class PostLineNulTest(PostNulTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = environ['wsgi.input'].readline()

            start_response("200 OK", [
                ("Content-Type", "application/octet-stream")
            ])
            return [data]

        return self.error(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

class PostExactReadNulTest(PostNulTestBase):
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            content_type, charset = parse_content_type(environ)
            if content_type != "application/x-www-form-urlencoded":
                return self.err(start_response,
                                "Didn't get expected Content-Type")

            data = environ['wsgi.input'].read(4)

            start_response("200 OK", [
                ("Content-Type", "application/octet-stream")
            ])
            return [data]

        return self.err(start_response, "Expected POST")

    def make_request(self, url):
        return requests.post(url, data=self.data())

    def expected_data(self):
        return self.data()[:4]
