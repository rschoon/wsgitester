
import sys
from . import *

class HelloTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        return [self.DATA.encode('utf-8')]

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.text != self.DATA:
            return TestFail("Didn't get expected text %r"%self.DATA)

class EmptyIterTest(Test):
    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        return []

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if len(resp.content) > 0:
            return TestFail("Expected empty content, but got %d bytes"%len(resp.content))

class ContentTypePNG(Test):
    DATA = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00' \
        b'\x00\x00\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00' \
        b'\x00\x0bIDAT\x18Wc``\x00\x00\x00\x03\x00\x01h&Y\r\x00\x00' \
        b'\x00\x00IEND\xaeB`\x82'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'image/png')])
        return [self.DATA]

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.content != self.DATA:
            return TestFail("Got %d bytes instead of expected response"%len(resp.content))

class ContentTypeJSON(Test):
    DATA = "{'var':'value','arr':[1,2,3]}"

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'application/json')])
        return [self.DATA.encode('utf-8')]

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.text != self.DATA:
            return TestFail("Got %d bytes instead of expected response"%len(resp.content))

class GeneratorTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        yield self.DATA.encode('utf-8')

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.text != self.DATA:
            return TestFail("Got %d bytes instead of expected response"%len(resp.content))

class BufferHeadersUntilNonEmptyTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        yield b''

        try:
            raise RuntimeError
        except RuntimeError:
            start_response('200 OK',
                       [('Content-type', 'text/plain')], sys.exc_info())
        yield self.DATA.encode('utf-8')

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.text != self.DATA:
            return TestFail("Got %d bytes instead of expected response"%len(resp.content))

class WriteTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        write = start_response('200 OK',
                   [('Content-type','text/plain')])
        write(self.DATA.encode('utf-8'))
        return []

    def verify(self, resp):
        if resp.status_code != 200:
            return TestFail("Got status code %d" % resp.status_code)

        if resp.text != self.DATA:
            return TestFail("Got %d bytes instead of expected response"%len(resp.content))
