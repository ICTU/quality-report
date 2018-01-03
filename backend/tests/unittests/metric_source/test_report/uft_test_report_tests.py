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

from hqlib.metric_source import UFTTestReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake URL opener. """
    contents = ''

    def url_read(self, url):
        """ Return the html or raise an exception. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return self.contents


class UFTTestReportTest(unittest.TestCase):
    """ Unit tests for the UFT test report class. """
    def setUp(self):
        self.__opener = FakeUrlOpener()
        for method in (UFTTestReport.datetime, UFTTestReport.failed_tests, UFTTestReport.skipped_tests,
                       UFTTestReport.passed_tests):
            method.cache_clear()
        self.__uft = UFTTestReport(url_read=self.__opener.url_read)

    def test_test_report(self):
        """ Test retrieving a UFT test report. """
        self.__opener.contents = '''<Report><Doc><Summary failed="1" passed="2"/></Doc></Report>'''
        self.assertEqual(1, self.__uft.failed_tests('url'))
        self.assertEqual(2, self.__uft.passed_tests('url'))
        self.assertEqual(0, self.__uft.skipped_tests('url'))

    def test_report_skipped(self):
        """ Test that the number of skipped tests can be parsed. """
        self.__opener.contents = """<Report><Step><Obj><![CDATA[ Stappenreferentie ]]></Obj>
            <Details><![CDATA[ 108 ]]></Details></Step>
            <Doc><Summary failed="1" passed="2"/></Doc></Report>"""
        self.assertEqual(105, self.__uft.skipped_tests('url'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.assertEqual(-1, self.__uft.failed_tests('raise'))
        self.assertEqual(-1, self.__uft.passed_tests('raise'))
        self.assertEqual(-1, self.__uft.skipped_tests('raise'))

    def test_missing_url(self):
        """ Test that the default is returned when no urls are provided. """
        self.assertEqual(-1, self.__uft.failed_tests())
        self.assertEqual(-1, self.__uft.passed_tests())
        self.assertEqual(-1, self.__uft.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__uft.datetime())

    def test_incomplete_xml(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__opener.contents = '<Report></Report>>'
        self.assertEqual(-1, self.__uft.failed_tests('url'))

    def test_faulty_xml(self):
        """ Test incorrect XML. """
        self.__opener.contents = '<foo><bar>'
        self.assertEqual(-1, self.__uft.failed_tests('url'))

    def test_missing_step_reference(self):
        """ Test that the number of skipped tests returns -1 when the step reference can't be parsed. """
        self.__opener.contents = """<Report><Step><Obj><![CDATA[ Stappenreferentie ]]></Obj>
            <Details></Details></Step>
            <Doc><Summary failed="1" passed="2"/></Doc></Report>"""
        self.assertEqual(-1, self.__uft.skipped_tests('url'))

    def test_faulty_step_reference(self):
        """ Test that the number of skipped tests returns -1 when the step reference can't be parsed. """
        self.__opener.contents = """<Report><Step><Obj></Obj>
            <Details><![CDATA[ 108 ]]></Details></Step>
            <Doc><Summary failed="1" passed="2"/></Doc></Report>"""
        self.assertEqual(0, self.__uft.skipped_tests('url'))

    def test_passed_larget_than_step_reference(self):
        """ Test that the number of skipped tests returns 0 when the step reference is lower than the sum of passed and
            failed tests. Assume the step reference wasn't updated after tests were added and the number of skipped
            tests is zero. """
        self.__opener.contents = """<Report><Step><Obj><![CDATA[ Stappenreferentie ]]></Obj>
            <Details>10</Details></Step>
            <Doc><Summary failed="1" passed="20"/></Doc></Report>"""
        self.assertEqual(0, self.__uft.skipped_tests('url'))

    def test_datetime_with_faulty_xml(self):
        """ Test incorrect XML. """
        self.__opener.contents = '<foo><bar>'
        self.assertEqual(datetime.datetime.min, self.__uft.datetime('url'))

    def test_report_datetime(self):
        """ Test that the date and time of the test suite is returned. """
        self.__opener.contents = '''<Report><Doc><Summary eTime="5-9-2017 - 14:18:23"/></Doc></Report>'''
        self.assertEqual(datetime.datetime(2017, 9, 5, 14, 18, 23), self.__uft.datetime('url'))

    def test_missing_report_datetime(self):
        """ Test that the minimum datetime is returned if the url can't be opened. """
        self.assertEqual(datetime.datetime.min, self.__uft.datetime('raise'))

    def test_incomplete_xml_datetime(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<Report></Report>'
        self.assertEqual(datetime.datetime.min, self.__uft.datetime('url'))

    def test_incomplete_xml_no_timestamp(self):
        """ Test that the minimum datetime is returned when the xml is incomplete. """
        self.__opener.contents = '<Report><Doc><Summary/></Doc></Report>'
        self.assertEqual(datetime.datetime.min, self.__uft.datetime('url'))

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        # Points to the XML at the moment because the UFT HTML report isn't stored at a predictable location.
        self.assertEqual(['http://server/uft/uft.xml'],
                         self.__uft.metric_source_urls('http://server/uft/uft.xml'))
