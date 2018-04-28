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

from hqlib.metric_source import Checkmarx


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static json. """
    json = '{"value": [{"LastScan": {"High": 0, "Medium": 1, "ScanCompletedOn": "2017-09-20T00:43:35.73+01:00"}}]}'

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
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('raise'))

    def test_url(self):
        """ Test the metric source base url. """
        self.assertEqual("http://url/", self.__report.url())

    def test_datetime(self):
        """ Test the date and time of the report. """
        self.assertEqual(datetime.datetime(2017, 9, 20, 0, 43, 35), self.__report.datetime('id'))

    def test_datetime_missing(self):
        """ Test a missing date and time of the report. """
        self.__opener.json = '{}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))

    def test_datetime_when_code_unchanged(self):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        self.__opener.json = '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
                             '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
                             'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 26, 12, 30, 24), self.__report.datetime('id'))

    def test_datetime_when_code_unchanged_multiple_times(self):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        self.__opener.json = '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
                             '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
                             'were detected; Attempt to perform scan on 9/27/2017 12:30:24 PM - No code changes ' \
                             'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 27, 12, 30, 24), self.__report.datetime('id'))

    def test_datetime_when_some_checks_have_no_date(self):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        self.__opener.json = '{"value": [{"LastScan": {"ScanCompletedOn": "2016-12-14T00:01:30.737+01:00", ' \
                             '"Comment": "Attempt to perform scan on 2/13/2017 8:00:06 PM - No code changes were ' \
                             'detected;  No code changes were detected No code changes were detected"}}]}'
        self.assertEqual(datetime.datetime(2017, 2, 13, 20, 0, 6), self.__report.datetime('id'))

    def test_nr_warnings_on_missing_values(self):
        """ Test dealing with empty list of values. """
        self.__opener.json = '{"value": []}'
        self.assertEqual(-1, self.__report.nr_warnings(['id'], 'medium'))

    def test_datetime_on_missing_values(self):
        """ Test dealing with empty list of values. """
        self.__opener.json = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))

    def test_datetime_on_url_exception(self):
        """ Test dealing with empty list of values. """
        self.__opener.json = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('raise'))
