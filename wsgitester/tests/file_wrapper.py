
import sys

from six import BytesIO

from . import *

class FileWrapperTest(Test):
    abstract = True

    def __call__(self, environ, start_response):
        if 'wsgi.file_wrapper' not in environ:
            start_response('200 OK', [
                ('Content-type', 'text/plain'),
                ('X-Test', 'skip')
            ])
            return []
        return self.handle(environ, start_response)
    
    def verify(self, resp):
        if resp.headers.get('X-Test') == "skip":
            return TestSkip()
        return self.verify_noskip(resp)

class BytesIOTest(FileWrapperTest):
    DATA = b'hello, world!'

    def handle(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])

        val = BytesIO(self.DATA)
        return environ['wsgi.file_wrapper'](val, 2**8)

    def verify_noskip(self, resp):
        if resp.content != self.DATA:
            return TestFail("Got %r for data"%(resp.content, ))
