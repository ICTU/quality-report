"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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
import urllib.error

from hqlib.metric_source import Checkmarx


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static json. """
    json = '{"value": [{"LastScan": {"High": 0, "Medium": 1}}]}'

    def url_read(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib.error.HTTPError(url, None, None, None, None)
        else:
            return self.json


class CheckmarxTest(unittest.TestCase):
    """ Unit tests for the Checkmarx class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__report = Checkmarx('http://url', 'username', 'password', url_open=self.__opener)

    def test_high_risk_warnings(self):
        """ Test the number of high risk warnings. """
        self.assertEqual(0, self.__report.nr_warnings(['id'], 'high'))

    def test_medium_risk_warnins(self):
        """ Test the number of medium risk warnings. """
        self.assertEqual(1, self.__report.nr_warnings(['id'], 'medium'))

    def test_passed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.nr_warnings(['raise'], 'high'))

    def test_multiple_urls(self):
        """ Test the number of alerts for multiple urls. """
        self.assertEqual(2, self.__report.nr_warnings(['id1', 'id2'], 'medium'))

    def test_metric_source_urls_without_report(self):
        """ Test the metric source urls without metric ids. """
        self.assertEqual([], self.__report.metric_source_urls())

    def test_metric_source_urls(self):
        """ Test the metric source urls with one metric id. """
        self.assertEqual([], self.__report.metric_source_urls('id'))

    def test_metric_source_urls_on_error(self):
        """ Test the metric source urls when an error occurs. """
        self.assertEqual([], self.__report.metric_source_urls('raise'))

    def test_url(self):
        """ Test the metric source base url. """
        self.assertEqual('http://url', self.__report.url())

