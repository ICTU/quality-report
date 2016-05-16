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

from qualitylib.metric_source import JenkinsTestReport


class FakeUrlOpener(object):
    """ Fake URL opener. """
    contents = u'{}'

    def url_open(self, url):
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return io.StringIO(self.contents)


class JenkinsTestReportTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """ Unit tests for the Jenkins test report class. """
    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__jenkins = JenkinsTestReport(url_open=self.__opener.url_open)

    def test_testreport(self):
        """ Test retrieving a Jenkins test report. """
        self.__opener.contents = u'{"failCount":2, "passCount":9, "skipCount":1}'
        self.assertEqual(2, self.__jenkins.failed_tests('job'))
        self.assertEqual(9, self.__jenkins.passed_tests('job'))
        self.assertEqual(1, self.__jenkins.skipped_tests('job/'))

    def test_testreport_without_pass_count(self):
        """ Test retrieving a Jenkins test report that has no pass count.
            Apparently that field is not present when there are no tests. """
        self.__opener.contents = u'{"failCount":0, "skipCount":0, "totalCount":8}'
        self.assertEqual(0, self.__jenkins.failed_tests('job/'))
        self.assertEqual(8, self.__jenkins.passed_tests('job'))
        self.assertEqual(0, self.__jenkins.skipped_tests('job'))

    def test_http_error(self):
        """ Test that the default is returned when a HTTP error occurs. """
        self.assertEqual(-1, self.__jenkins.failed_tests('raise'))
        self.assertEqual(-1, self.__jenkins.passed_tests('raise'))
        self.assertEqual(-1, self.__jenkins.skipped_tests('raise'))

    def test_eval_exception(self):
        """ Test that the default is returned when the json can't be parsed. """
        self.__opener.contents = u'{"failCount":, "passCount":9, "skipCount":1}'
        self.assertEqual(-1, self.__jenkins.failed_tests('job'))
