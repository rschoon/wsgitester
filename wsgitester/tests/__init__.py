
from collections import OrderedDict
import requests
import six


__all__ = ['test_lookup', 'Test']

class TestLookup(object):
    def __init__(self, *test_imports):
        self.test_imports = test_imports
        self.tests = None

    def register(self, cls):
        cls.name = "%s.%s"%(cls.__module__, cls.__name__)
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

class TestMeta(type):
    def __init__(self, name, bases, data):
        super(TestMeta, self).__init__(name, bases, data)
        if 'abstract' not in data:
            test_lookup.register(self)

@six.add_metaclass(TestMeta)
class Test(object):
    abstract = True

    def run(self, ctx):
        r = requests.get(ctx.test_url(self.name))
        return self.verify(r)

#
#
#

test_lookup = TestLookup(
    'wsgitester.tests.basic'
)


