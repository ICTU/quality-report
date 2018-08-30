"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime
import unittest
from unittest.mock import Mock
import urllib.error

from hqlib.metric_source import JunitTestReport


class JunitTestReportTest(unittest.TestCase):
    """ Unit tests for the Junit test report class. """

    # pylint: disable=protected-access

    def setUp(self):
        self.__junit = JunitTestReport()

    def test_test_report(self):
        """ Test retrieving a Junit test report. """
        self.__junit._url_read = Mock(
            return_value='<testsuites>'
                         '  <testsuite tests="12" failures="2" errors="0" skipped="1" disabled="0">'
                         '    <testcase><failure/></testcase>'
                         '    <testcase><failure/></testcase>'
                         '  </testsuite>'
                         '</testsuites>')
        self.assertEqual(2, self.__junit.failed_tests('url'))
        self.assertEqual(9, self.__junit.passed_tests('url'))
        self.assertEqual(1, self.__junit.skipped_tests('url'))

    def test_multiple_test_suites(self):
        """ Test retrieving a Junit test report with multiple suites. """
        self.__junit._url_read = Mock(
            return_value='<testsuites>'
                         '  <testsuite tests="5" failures="1" errors="0" skipped="1" disabled="1">'
                         '    <testcase><failure/><failure/></testcase>'
                         '  </testsuite>'
                         '  <testsuite tests="3" failures="1" errors="1" skipped="0" disabled="0">'
                         '    <testcase><failure/></testcase>'
                         '  </testsuite>'
                         '</testsuites>')
        self.assertEqual(3, self.__junit.failed_tests('url'))
        self.assertEqual(3, self.__junit.passed_tests('url'))
        self.assertEqual(2, self.__junit.skipped_tests('url'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.__junit._url_read = Mock(side_effect=urllib.error.HTTPError(None, None, None, None, None))
        self.assertEqual(-1, self.__junit.failed_tests('raise'))
        self.assertEqual(-1, self.__junit.passed_tests('raise'))
        self.assertEqual(-1, self.__junit.skipped_tests('raise'))

    def test_missing_url(self):
        """ Test that the default is returned when no urls are provided. """
        self.assertEqual(-1, self.__junit.failed_tests())
        self.assertEqual(-1, self.__junit.passed_tests())
        self.assertEqual(-1, self.__junit.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__junit.datetime())

    def test_incomplete_xml(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__junit._url_read = Mock(return_value='<testsuites></testsuites>')
        self.assertEqual(-1, self.__junit.failed_tests('url'))

    def test_faulty_xml(self):
        """ Test incorrect XML. """
        self.__junit._url_read = Mock(return_value='<testsuites><bla>')
        self.assertEqual(-1, self.__junit.failed_tests('url'))

    def test_datetime_with_faulty_xml(self):
        """ Test incorrect XML. """
        self.__junit._url_read = Mock(return_value='<testsuites><bla>')
        self.assertEqual(datetime.datetime.min, self.__junit.datetime('url'))

    def test_report_datetime(self):
        """ Test that the date and time of the test suite is returned. """
        self.__junit._url_read = Mock(
            return_value='<testsuites>'
                         '  <testsuite name="Art" timestamp="2016-07-07T12:26:44">'
                         '  </testsuite>'
                         '</testsuites>')
        self.assertEqual(datetime.datetime(2016, 7, 7, 12, 26, 44), self.__junit.datetime('url'))

    def test_missing_report_datetime(self):
        """ Test that the minimum datetime is returned if the url can't be opened. """
        self.__junit._url_read = Mock(side_effect=urllib.error.HTTPError(None, None, None, None, None))
        self.assertEqual(datetime.datetime.min, self.__junit.datetime('url'))

    def test_incomplete_xml_datetime(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__junit._url_read = Mock(return_value='<testsuites></testsuites>')
        self.assertEqual(datetime.datetime.min, self.__junit.datetime('url'))

    def test_incomplete_xml_no_timestamp(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__junit._url_read = Mock(return_value='<testsuites><testsuite></testsuite></testsuites>')
        self.assertEqual(datetime.datetime.min, self.__junit.datetime('url'))

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        self.assertEqual(['http://server/html/htmlReport.html'],
                         self.__junit.metric_source_urls('http://server/junit/junit.xml'))

    def test_url_regexp(self):
        """ Test that the default regular expression to generate the HTML version of the urls can be changed. """
        junit = JunitTestReport(metric_source_url_re="junit.xml$", metric_source_url_repl="junit.html")
        self.assertEqual(['http://server/junit.html'], junit.metric_source_urls('http://server/junit.xml'))
