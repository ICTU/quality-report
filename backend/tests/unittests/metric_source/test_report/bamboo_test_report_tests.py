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

from hqlib.metric_source import BambooTestReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake URL opener. """
    contents = ''

    def url_read(self, url):
        """ Return the html or raise an exception. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return self.contents


class BambooTestReportTest(unittest.TestCase):
    """ Unit tests for the Bamboo test report class. """
    def setUp(self):
        self.__opener = FakeUrlOpener()
        for method in (BambooTestReport.datetime, BambooTestReport.failed_tests, BambooTestReport.skipped_tests,
                       BambooTestReport.passed_tests):
            method.cache_clear()
        self.__report = BambooTestReport(url_read=self.__opener.url_read)

    def test_test_report(self):
        """ Test retrieving a Bamboo test report. """
        self.__opener.contents = '''<result><successfulTestCount>1973</successfulTestCount>
            <failedTestCount>17</failedTestCount>
            <quarantinedTestCount>0</quarantinedTestCount>
            <skippedTestCount>2</skippedTestCount></result>'''
        self.assertEqual(17, self.__report.failed_tests('url'))
        self.assertEqual(1973, self.__report.passed_tests('url'))
        self.assertEqual(2, self.__report.skipped_tests('url'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.assertEqual(-1, self.__report.failed_tests('raise'))
        self.assertEqual(-1, self.__report.passed_tests('raise'))
        self.assertEqual(-1, self.__report.skipped_tests('raise'))
        self.assertEqual(datetime.datetime.min, self.__report.datetime('raise'))

    def test_missing_url(self):
        """ Test that the default is returned when no urls are provided. """
        self.assertEqual(-1, self.__report.failed_tests())
        self.assertEqual(-1, self.__report.passed_tests())
        self.assertEqual(-1, self.__report.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__report.datetime())

    def test_incomplete_xml(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__opener.contents = '<result></result>'
        self.assertEqual(-1, self.__report.failed_tests('url'))

    def test_empty_tag(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__opener.contents = '<result><successfulTestCount></successfulTestCount></result>'
        self.assertEqual(-1, self.__report.passed_tests('url'))

    def test_faulty_xml(self):
        """ Test incorrect XML. """
        self.__opener.contents = '<foo><bar>'
        self.assertEqual(-1, self.__report.failed_tests('url'))
        self.assertEqual(datetime.datetime.min, self.__report.datetime('url'))

    def test_report_datetime(self):
        """ Test that the date and time of the test suite is returned. """
        self.__opener.contents = \
            '<result><buildCompletedDate>2017-10-12T03:39:21.840+02:00</buildCompletedDate></result>'
        tzinfo = datetime.timezone(offset=datetime.timedelta(hours=2))
        expected = datetime.datetime(2017, 10, 12, 3, 39, 21, 840000, tzinfo=tzinfo).astimezone().replace(tzinfo=None)
        self.assertEqual(expected, self.__report.datetime('url'))

    def test_incomplete_xml_datetime(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<result><buildCompletedDate></result>'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('url'))

    def test_incomplete_xml_no_timestamp(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<result><buildCompletedDate></buildCompletedDate></result>'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('url'))

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        # Points to the XML at the moment.
        self.assertEqual(['http://bamboo/rest/api/latest/result/PLAN/latest'],
                         self.__report.metric_source_urls('http://bamboo/rest/api/latest/result/PLAN/latest'))
