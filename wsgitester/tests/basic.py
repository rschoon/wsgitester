
from . import Test

class HelloTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        return [self.DATA.encode('utf-8')]

    def verify(self, response):
        assert response.text == self.DATA

class UnnamedArgsTest(Test):
    def __call__(self, *args):
        args[1]('200 OK', [('Content-type', 'text/plain')])
        if len(args) != 2:
            return [b"FAIL"]
        return [b"PASS"]

    def verify(self, response):
        assert response.text == "PASS"

class EmptyIterTest(Test):
    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        return []

    def verify(self, response):
        assert len(response.content) == 0

class ContentTypePNG(Test):
    DATA = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00' \
        b'\x00\x00\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00' \
        b'\x00\x0bIDAT\x18Wc``\x00\x00\x00\x03\x00\x01h&Y\r\x00\x00' \
        b'\x00\x00IEND\xaeB`\x82'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'image/png')])
        return [self.DATA]

    def verify(self, response):
        assert response.content == self.DATA

class ContentTypeJSON(Test):
    DATA = "{'var':'value','arr':[1,2,3]}"

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'application/json')])
        return [self.DATA.encode('utf-8')]

    def verify(self, response):
        assert response.text == self.DATA

class GeneratorTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        yield self.DATA.encode('utf-8')

    def verify(self, response):
        assert response.text == self.DATA

class EmptyBytesPreStartTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        yield b''
        start_response('200 OK',
                   [('Content-type', 'text/plain')])
        yield self.DATA.encode('utf-8')

    def verify(self, response):
        assert response.text == self.DATA

class WriteTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        write = start_response('200 OK',
                   [('Content-type','text/plain')])
        write(self.DATA.encode('utf-8'))
        return []

    def verify(self, response):
        assert response.text == self.DATA
