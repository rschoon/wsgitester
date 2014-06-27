
import argparse
import sys

from .tests import test_lookup

#
#
#

argparser = argparse.ArgumentParser(description="Test WSGI Servers")
argparser.add_argument('url')

#
#
#

class TestContext(object):
    def __init__(self, url):
        self.url = url

    def test_url(self, name):
        return "%s%s"%(self.url, name)

def main():
    args = argparser.parse_args()

    so = sys.stdout
    ctx = TestContext(args.url)

    for test in test_lookup:
        line = "%s"%test.name
        so.write(line)
        so.flush()

        rv = test().run(ctx)

        so.write(" "*(60-len(line)))
        if rv:
            so.write("PASS")
        else:
            so.write("FAIL")
        so.write("\n")

