
import re

from .tests import test_lookup

class Application(object):
    def __init__(self):
        self.test_lookup = test_lookup

    RE_TEST_PATH = re.compile(r'(?P<sn>^/?(?P<t>[^/]+))/')

    def try_test(self, environ, start_response):
        script_name = environ.get('SCRIPT_NAME', '')
        path_info = environ.get('PATH_INFO', '')

        m = self.RE_TEST_PATH.search(path_info)
        if m is None:
            return

        try:
            test = self.test_lookup[m.group("t")]()
        except KeyError:
            return

        sn = m.group("sn")
        environ['SCRIPT_NAME'] = script_name + sn
        environ['PATH_INFO'] = path_info[len(sn):]

        return test(environ, start_response)

    def __call__(self, env, s_r):
        resp = self.try_test(env, s_r)
        if resp is not None:
            return resp

        s_r('404 Not Found', [('Content-Type', 'text/plain')])
        return [
            b"404 Not Found\n\n",
            b"SN=", environ.get("SCRIPT_NAME").encode('utf-8'), b'\n',
            b"PI=", environ.get("PATH_INFO").encode('utf-8'), b'\n',
        ]

application = Application()
