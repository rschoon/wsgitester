
from . import Test

class HelloTest(Test):
    DATA = 'Hello, World.\n'

    def __call__(self, environ, start_response):
        start_response('200 OK', 
                   [('Content-type','text/plain')])
        return [self.DATA.encode('utf-8')]
        
    def verify(self, response):
        return response.text == self.DATA

