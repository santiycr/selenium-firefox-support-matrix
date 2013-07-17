#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import new
import json
import unittest
from time import sleep
import argparse

from selenium import webdriver
import nose
from nose.plugins.multiprocess import MultiProcess

from lib.parse_version import parse_version

USER = os.environ['SAUCE_USER']
KEY = os.environ['SAUCE_KEY']
HOST = 'ondemand.saucelabs.com'
PORT = 80
JAR_URL = "https://sauce-bundles.s3.amazonaws.com/selenium/selenium-server-%s%s.jar"


class FirefoxSupportTest(unittest.TestCase):
    __test__ = False

    def setUp(self):
        parsed_version = parse_version(self.sel_version)
        jar_addition = ''
        if parsed_version <= (2, 19, 0):
            jar_addition += '-newcert'
        if (2, 14, 0) <= parsed_version <= (2, 25, 0):
            jar_addition += '-dnsfix'
        dc = {'platform': self.platform,
              'browserName': self.br,
              'version': self.version,
              'selenium-version': JAR_URL % (self.sel_version, jar_addition),
              'name': self.name,
              'prevent-requeue': True,
              }
        self.native = False
        try:
            self.driver = webdriver.Remote(desired_capabilities=dc,
                                           command_executor="http://%s:%s@%s:%s/wd/hub" %
                                           (USER, KEY, HOST, PORT))
        except Exception:
            self.driver = None
        else:
            self.native = self.driver.capabilities['nativeEvents']

    def test_browser_works(self):
        if not self.driver:
            self.fail("Failed to launch browser")
        for url in ['https://saucelabs.com', 'http://google.com']:
            self.driver.get(url)
            for i in range(30):
                if self.driver.title:
                    break
                sleep(0.5)
            else:
                self.fail("title never showed")

    def tearDown(self):
        if self.driver:
            self.driver.quit()
        with open(os.path.join(self.platform, '%s_%s_results.json' % (self.version,
                                                                      self.sel_version)),
                  'w') as results_file:
            results = {self.version: {
                self.sel_version: {
                    'worked': sys.exc_info() == (None, None, None),
                    'native': self.native}}}
            results_file.write(json.dumps(results))


parser = argparse.ArgumentParser(
    description='Collect Firefox vs Selenium version support matrix')
parser.add_argument('--firefox', '-f', metavar='FF_VER',
                    nargs='*', help='Specific versions of Firefox to test')
parser.add_argument('--selenium', '-s', metavar='SE_VER',
                    nargs='*', help='Specific versions of Selenium to test')
parser.add_argument('--platform', '-p', type=str, default="Windows 2003",
                    help='The OS to run the tests on.')
parser.add_argument('--threads', '-t', type=int, default=10,
                    help='Amount of threads to run tests in parallel on.')
args = parser.parse_args()

jars_to_test = args.selenium if args.selenium else [
    '2.0.0', '2.1.0', '2.2.0', '2.3.0', '2.4.0', '2.5.0', '2.6.0', '2.7.0',
    '2.8.0', '2.9.0', '2.10.0', '2.11.0', '2.12.0', '2.13.0', '2.14.0',
    '2.14.1', '2.15.0', '2.16.0', '2.16.1', '2.17.0', '2.18.0', '2.19.0',
    '2.20.0', '2.21.0', '2.22.0', '2.23.0', '2.23.1', '2.24.0', '2.24.1',
    '2.25.0', '2.26.0', '2.27.0', '2.28.0', '2.29.0', '2.30.0', '2.31.0',
    '2.32.0', '2.33.0',
]
firefoxes_to_test = args.firefox if args.firefox else range(3, 23)
classes = {}
for jar_version in jars_to_test:
    for ff_version in firefoxes_to_test:
        name = "%s_%s_%s" % (FirefoxSupportTest.__name__, jar_version, ff_version)
        name = name.encode('ascii')
        if name.endswith("."):
            name = name[:-1]
        for x in ". ":
            name = name.replace(x, "")

        d = dict(FirefoxSupportTest.__dict__)
        d.update({'__test__': True,
                  '__name__': name,
                  'name': name,
                  'platform': args.platform,
                  'br': 'firefox',
                  'version': ff_version,
                  'sel_version': jar_version,
                  })

        classes[name] = new.classobj(name, (FirefoxSupportTest,), d)
globals().update(classes)

if __name__ == "__main__":
    if not os.path.isdir(args.platform):
        os.mkdir(args.platform)
    nose.core.run(argv=['--nocapture', "-v", "--processes", args.threads,
                        "--process-timeout", "1800", __file__],
                  plugins=[MultiProcess()])
