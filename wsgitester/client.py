
import argparse
import sys

from .tests import *

#
#
#

argparser = argparse.ArgumentParser(description="Test WSGI Servers")
argparser.add_argument('--skip')
argparser.add_argument('url')

#
#
#

class TestContext(object):
    def __init__(self, url, skiplist):
        self.url = url
        self.skiplist = skiplist

    def test_url(self, name):
        return "%s%s"%(self.url, name)

def run_test(ctx, test):
    if test.name in ctx.skiplist:
        return TestSkip()

    return test().run(ctx)

def run_all_tests(ctx, stdout=None):
    if stdout is None:
        stdout = sys.stdout

    for test in test_lookup:
        line = "%s"%test.name
        stdout.write(line)
        stdout.flush()

        try:
            result = run_test(ctx, test)
        except Exception as e:
            # TODO catch and handle inside run_test
            stdout.write("\n")
            raise
        
        stdout.write(" "*(60-len(line)))
        if result:
            if isinstance(result, TestSkip):
                stdout.write("SKIP")
            else:
                stdout.write("PASS")
        else:
            stdout.write("FAIL")
        stdout.write("\n")

        if result.msg:
            stdout.write("    %s\n"%(result.msg,))

def main():
    args = argparser.parse_args()

    if args.skip:
        skiplist = [s.strip() for s in args.skip.split(",")]
    else:
        skiplist = []

    run_all_tests(TestContext(args.url, skiplist))
