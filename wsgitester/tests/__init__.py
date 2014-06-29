
from collections import OrderedDict
import requests
import six


__all__ = ['test_lookup', 'Test', 'TestFail', 'TestPass', 'TestSkip']

class TestLookup(object):
    def __init__(self, *test_imports):
        self.test_imports = test_imports
        self.tests = None

    def register(self, cls):
        cls.name = "%s:%s"%(cls.__module__, cls.__name__)
        self.tests[cls.name] = cls

    def load_tests(self):
        self.tests = OrderedDict()
        for mname in self.test_imports:
            __import__(mname)

    def __getitem__(self, name):
        if self.tests is None:
            self.load_tests()
        return self.tests[name]

    def __iter__(self):
        if self.tests is None:
            self.load_tests()
        return iter(self.tests.values())

#
#
#

class TestResult(object):
    def __init__(self, msg=None):
        self.msg = msg

    def __bool__(self):
        return True

    def __nonzero__(self):
        return True

class TestFail(TestResult):
    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

class TestPass(TestResult):
    pass

class TestSkip(TestResult):
    pass


#
#
#

class TestMeta(type):
    def __init__(self, name, bases, data):
        super(TestMeta, self).__init__(name, bases, data)
        if 'abstract' not in data:
            test_lookup.register(self)

@six.add_metaclass(TestMeta)
class Test(object):
    abstract = True

    def make_request(self, url):
        return requests.get(url)

    def run(self, ctx):
        resp = self.make_request(ctx.test_url(self.name))
        result = self.verify(resp)
        if isinstance(result, bool) or result is None:
            if result:
                return TestPass()
            else:
                return TestFail()
        return result

    def verify(self, response):
        raise NotImplementedError

#
#
#

test_lookup = TestLookup(
    'wsgitester.tests.basic',
    'wsgitester.tests.types',
    'wsgitester.tests.input'
)


