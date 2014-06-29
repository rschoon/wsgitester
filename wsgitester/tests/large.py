
from . import *

class ManyChunksTest(Test):
    """This deliberately tends to be a slow test."""

    def __call__(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        for i in range(32768):
            yield b'0123456789abcdef'*8

    def verify(self, resp):
        if len(resp.content) != 1024*256*16:
            return TestFail("Invalid result size (%d bytes)." %
                            (len(resp.content),))

        for i in range(1024*256, 16):
            if resp.content[i:i+16] != b'0123456789abcdef':
                return TestFail("Invalid bytes near offset %d." % i)

        return TestPass()

class LargeChunkTest(Test):
    def __call__(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        return [b'0123456789abcdef'*(1024*1024)]

    def verify(self, resp):
        if len(resp.content) != 1024*1024*16:
            return TestFail("Invalid result size (%d bytes)." %
                            (len(resp.content),))

        for i in range(1024*1024, 16):
            if resp.content[i:i+16] != b'0123456789abcdef':
                return TestFail("Invalid bytes near offset %d." % i)

        return TestPass()

class LargeOffsettedChunkTest(Test):
    def __call__(self, environ, start_response):
        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        return [b'0123456789', b'0123456789abcdef'*(1024*1024)]

    def verify(self, resp):
        if len(resp.content) != 1024*1024*16 + 10:
            return TestFail("Invalid result size.")

        if resp.content[:10] != b"0123456789":
            return TestFail("Invalid bytes at start of content")

        for i in range(1024*256, 16):
            if resp.content[i+10:i+26] != b'0123456789abcdef':
                return TestFail("Invalid bytes near offset %d." % i)

        return TestPass()
