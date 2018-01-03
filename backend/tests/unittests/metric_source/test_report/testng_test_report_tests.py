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
import urllib.error

from hqlib.metric_source import TestNGTestReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake URL opener. """
    contents = ''

    def url_read(self, url):
        """ Return the html or raise an exception. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return self.contents


class TestNGTestReportTest(unittest.TestCase):
    """ Unit tests for the TestNG test report class. """
    def setUp(self):
        self.__opener = FakeUrlOpener()
        for method in (TestNGTestReport.datetime, TestNGTestReport.failed_tests, TestNGTestReport.skipped_tests,
                       TestNGTestReport.passed_tests):
            method.cache_clear()
        self.__testng = TestNGTestReport(url_read=self.__opener.url_read)

    def test_test_report(self):
        """ Test retrieving a TestNG test report. """
        self.__opener.contents = '''<testng-results skipped="0" failed="1" ignored="3" total="6" passed="2">
<suite name="TestSuite" duration-ms="6548" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:29Z">
<test name="engine" duration-ms="3474" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:26Z">
<class name="CreatingARegistratie"></class>
</test>
<test name="beheer" duration-ms="6548" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:29Z">
<class name="LookingUpARegistratie"></class>
<class name="LookingUpRegistratiesOverview"></class>
</test>
</suite>
</testng-results>'''
        self.assertEqual(1, self.__testng.failed_tests('url'))
        self.assertEqual(2, self.__testng.passed_tests('url'))
        self.assertEqual(0, self.__testng.skipped_tests('url'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.assertEqual(-1, self.__testng.failed_tests('raise'))
        self.assertEqual(-1, self.__testng.passed_tests('raise'))
        self.assertEqual(-1, self.__testng.skipped_tests('raise'))

    def test_missing_url(self):
        """ Test that the default is returned when no urls are provided. """
        self.assertEqual(-1, self.__testng.failed_tests())
        self.assertEqual(-1, self.__testng.passed_tests())
        self.assertEqual(-1, self.__testng.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__testng.datetime())

    def test_incomplete_xml(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__opener.contents = '<testng-results></testng-results>'
        self.assertEqual(-1, self.__testng.failed_tests('url'))

    def test_faulty_xml(self):
        """ Test incorrect XML. """
        self.__opener.contents = '<foo><bar>'
        self.assertEqual(-1, self.__testng.failed_tests('url'))

    def test_datetime_with_faulty_xml(self):
        """ Test incorrect XML. """
        self.__opener.contents = '<testng-results><bla></testng-results>'
        self.assertEqual(datetime.datetime.min, self.__testng.datetime('url'))

    def test_report_datetime(self):
        """ Test that the date and time of the test suite is returned. """
        self.__opener.contents = '''<testng-results skipped="0" failed="1" ignored="3" total="6" passed="2">
<suite name="TestSuite" duration-ms="6548" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:29Z">
<test name="engine" duration-ms="3474" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:26Z">
<class name="CreatingARegistratie"></class>
</test>
<test name="beheer" duration-ms="6548" started-at="2017-09-05T14:18:23Z" finished-at="2017-09-05T14:18:29Z">
<class name="LookingUpARegistratie"></class>
<class name="LookingUpRegistratiesOverview"></class>
</test>
</suite>
</testng-results>'''
        self.assertEqual(datetime.datetime(2017, 9, 5, 14, 18, 23), self.__testng.datetime('url'))

    def test_missing_report_datetime(self):
        """ Test that the minimum datetime is returned if the url can't be opened. """
        self.assertEqual(datetime.datetime.min, self.__testng.datetime('raise'))

    def test_incomplete_xml_datetime(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<testng-results></testng-results>'
        self.assertEqual(datetime.datetime.min, self.__testng.datetime('url'))

    def test_incomplete_xml_no_timestamp(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<testng-results><suite></suite></testng-results>'
        self.assertEqual(datetime.datetime.min, self.__testng.datetime('url'))

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        # Points to the XML at the moment because the TestNG HTML report isn't stored at a predictable location.
        self.assertEqual(['http://server/testng/testng.xml'],
                         self.__testng.metric_source_urls('http://server/testng/testng.xml'))
