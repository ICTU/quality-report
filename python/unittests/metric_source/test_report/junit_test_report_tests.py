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

import io
import unittest
import urllib2

from qualitylib.metric_source import JunitTestReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake URL opener. """
    contents = u''

    def url_open(self, url):
        """ Return the html or raise an exception. """
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(self.contents)


class JunitTestReportTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Junit test report class. """
    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__jenkins = JunitTestReport(url_open=self.__opener.url_open)

    def test_test_report(self):
        """ Test retrieving a Junit test report. """
        self.__opener.contents = u'<testsuites>' \
                                 '  <testsuite tests="12" failures="2" errors="0" skipped="1" disabled="0">' \
                                 '  </testsuite>' \
                                 '</testsuites>'
        self.assertEqual(2, self.__jenkins.failed_tests('url'))
        self.assertEqual(9, self.__jenkins.passed_tests('url'))
        self.assertEqual(1, self.__jenkins.skipped_tests('url'))

    def test_multiple_test_suites(self):
        """ Test retrieving a Junit test report with multiple suites. """
        self.__opener.contents = u'<testsuites>' \
                                 '  <testsuite tests="5" failures="1" errors="0" skipped="1" disabled="1">' \
                                 '  </testsuite>' \
                                 '  <testsuite tests="3" failures="1" errors="1" skipped="0" disabled="0">' \
                                 '  </testsuite>' \
                                 '</testsuites>'
        self.assertEqual(3, self.__jenkins.failed_tests('url'))
        self.assertEqual(3, self.__jenkins.passed_tests('url'))
        self.assertEqual(2, self.__jenkins.skipped_tests('url'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.assertEqual(-1, self.__jenkins.failed_tests('raise'))
        self.assertEqual(-1, self.__jenkins.passed_tests('raise'))
        self.assertEqual(-1, self.__jenkins.skipped_tests('raise'))

    def test_incomplete_xml(self):
        """ Test that the default is returned when the xml is incomplete. """
        self.__opener.contents = u'<testsuites></testsuites>'
        self.assertEqual(-1, self.__jenkins.failed_tests('url'))
