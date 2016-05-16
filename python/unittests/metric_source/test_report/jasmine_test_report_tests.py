"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import urllib2

from qualitylib.metric_source import JasmineHTMLReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static html. """
    html = '<div><h2><u>Results summary</u></h2>' \
           '<b>Total tests passed</b>: 123 <br/> ' \
           '<b>Total tests failed</b>: 13 <br/> ' \
           'This report generated on Fri Aug 21 2015 07:45:52 GMT+0000 (UTC) </div>'

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            return self.html


class JasmineHTMLReportTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Jasmine HTML report class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__report = JasmineHTMLReport(url_open=self.__opener.url_open)

    def test_passed(self):
        """ Test the number of tests passed for a specific report. """
        self.assertEqual(123, self.__report.passed_tests('product_report'))

    def test_failed(self):
        """ Test the number of tests passed for a specific report. """
        self.assertEqual(13, self.__report.failed_tests('product_report'))

    def test_skipped(self):
        """ Test the number of tests skipped for a specific report. """
        self.assertEqual(0, self.__report.skipped_tests('product_report'))

    def test_passed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.passed_tests('raise'))

    def test_failed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.failed_tests('raise'))

