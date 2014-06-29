
from . import Test

class EnvironTypes(Test):
    REQUIRED = ["REQUEST_METHOD", "SERVER_NAME", "SERVER_PORT",
                "wsgi.version", "wsgi.url_scheme", "wsgi.input",
                "wsgi.errors", "wsgi.multithread",
                "wsgi.multiprocess"]

    def __call__(self, environ, start_response):
        def err(msg):
            start_respone("200 OK", [("Content-Type", "text/plain")])
            return [msg.encode('utf-8')]

        if not isinstance(environ, dict):
            return err("environ is not a dict, but instead a `%s'" % type(environ).__name__)

        for ek, ev in environ.items():
            if not isinstance(ek, str):
                return err("found an invalid environ key: %s" % repr(ek))

            func = self.get_self_test(ek)
            if func is not None:
                e = func(ev)
                if e is not None:
                    return err(e)
            elif ek.startswith("HTTP_"):
                if not isinstance(ev, str):
                    return err("found invalid HTTP_ environ value: %s" % repr(ev))

        for reqenv in self.REQUIRED:
            if reqenv not in environ:
                return err("%s is missing from environ" % reqenv)

        start_response('200 OK',
                       [('Content-type', 'text/plain')])
        return [b"PASS"]

    def get_self_test(self, envname):
        if envname.startswith("wsgi_"):
            # avoid collision with our internal test name
            return None
        elif envname.startswith("wsgi."):
            envname = "wsgi_" + envname[5:]

        return getattr(self, "environ_" + envname, None)

    def environ_REQUEST_METHOD(self, value):
        if not isinstance(value, str):
            return "REQUEST_METHOD is not a string: %s" % repr(value)
        if len(value) == 0:
            return "REQUEST_METHOD is empty"

    def environ_SCRIPT_NAME(self, value):
        # XXX check for ending or starting slashes??
        if not isinstance(value, str):
            return "SCRIPT_NAME is not a string: %s" % repr(value)

    def environ_PATH_INFO(self, value):
        # XXX check for starting slash?
        if not isinstance(value, str):
            return "PATH_INFO is not a string: %s" % repr(value)

    def environ_QUERY_STRING(self, value):
        if not isinstance(value, str):
            return "QUERY_STRING is not a string: %s" % repr(value)

    def environ_CONTENT_TYPE(self, value):
        if not isinstance(value, str):
            return "CONTENT_TYPE is not a string: %s" % repr(value)

    def environ_CONTENT_LENGTH(self, value):
        if not isinstance(value, str):
            return "CONTENT_LENGTH is not a string: %s" % repr(value)

        if len(value) > 0:
            try:
                i = int(value)
            except ValueError:
                return "CONTENT_LENGTH is not an integer string: %s" % repr(value)

    def environ_SERVER_NAME(self, value):
        if not isinstance(value, str):
            return "SERVER_NAME is not a string: %s" % repr(value)
        if len(value) == 0:
            return "SERVER_NAME is empty"

    def environ_SERVER_PORT(self, value):
        if not isinstance(value, str):
            return "SERVER_PORT is not a string: %s" % repr(value)
        if len(value) == 0:
            return "SERVER_PORT is empty"

        try:
            i = int(value)
        except ValueError:
            return "SERVER_PORT is not an integer string: %s" % repr(value)

    def environ_SERVER_PROTOCOL(self, value):
        # Note: We could have an "empty protocol string" as a protocol
        # so we don't actually check to make sure it is provided.
        if not isinstance(value, str):
            return "SERVER_PROTOCOL is not a string: %s" % repr(value)

    def environ_wsgi_version(self, value):
        if not isinstance(value, tuple):
            return "wsgi.version is not a tuple: %s" % repr(value)

        if len(value) < 2:
            return "wsgi.version's size is too small: %s" % repr(value)

        # I'm not suggesting this is an error with the WSGI gateway, but
        # we're not really remotely in a position to check a server
        # identifying itself as 2.x
        if value[0] != 1:
            return "wsgi.version indicates server is not 1.x"

    def environ_wsgi_url_scheme(self, value):
        if not isinstance(value, str):
            return "wsgi.url_scheme is not a string: %s" % repr(value)
        elif value.lower() not in ("http", "https"):
            return "wsgi.url_scheme is not one of http or https: %s" % repr(value)

    def environ_wsgi_input(self, value):
        if not callable(getattr(value, "read", None)):
            return "wsgi.input lacks a read method"
        elif not callable(getattr(value, "readline")):
            return "wsgi.input lacks a readline method"
        elif not callable(getattr(value, "readlines")):
            return "wsgi.input lacks a readlines method"
        elif not callable(getattr(value, "__iter__")):
            return "wsgi.input lacks an __iter__ method"

    def environ_wsgi_errors(self, value):
        if not callable(getattr(value, "flush", None)):
            return "wsgi.errors lacks a flush method"
        elif not callable(getattr(value, "write", None)):
            return "wsgi.errors lacks a write method"
        elif not callable(getattr(value, "writelines", None)):
            return "wsgi.errors lacks a writelines method"

    def environ_wsgi_file_wrapper(self, value):
        if not callable(value):
            return "wsgi.file_wrapper is not callable"

    def verify(self, response):
        return response.text.startswith("PASS")
