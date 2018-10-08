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

import ssl
import logging
import datetime
import urllib.error
import unittest
from unittest.mock import patch, call

from hqlib.metric_source import Checkmarx, url_opener


LAST_SCAN = '{"value": [{"LastScan": {"High": 0, "Medium": 1, "ScanCompletedOn": "2017-09-20T00:43:35.73+01:00"}}]}'


@patch.object(url_opener.UrlOpener, 'url_read')
class CheckmarxTest(unittest.TestCase):
    """ Unit tests for the Checkmarx class. """

    def setUp(self):
        self.__report = Checkmarx('http://url', 'username', 'password')

    def test_high_risk_warnings(self, mock_url_read):
        """ Test the number of high risk warnings. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(0, self.__report.nr_warnings(['id'], 'high'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    @patch('ssl._create_unverified_context')
    def test_nr_warnings_legacy_ssl(self, mock_create_unverified_context, mock_url_read):
        """ Test the number of high risk warnings with legacy python ssl. """
        delattr(ssl, '_create_unverified_context')
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(0, self.__report.nr_warnings(['id'], 'high'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')
        mock_create_unverified_context.assert_not_called()

    def test_medium_risk_warnins(self, mock_url_read):
        """ Test the number of medium risk warnings. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(1, self.__report.nr_warnings(['id'], 'medium'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_passed_raise(self, mock_url_read):
        """ Test that the value is -1 when the report can't be opened. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.assertEqual(-1, self.__report.nr_warnings(['raise'], 'high'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27raise%27')

    def test_multiple_urls(self, mock_url_read):
        """ Test the number of alerts for multiple urls. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(2, self.__report.nr_warnings(['id1', 'id2'], 'medium'))
        self.assertEqual([
            call('http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id1%27'),
            call('http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id2%27')
        ], mock_url_read.call_args_list)

    def test_metric_source_urls_without_report(self, mock_url_read):
        """ Test the metric source urls without metric ids. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual([], self.__report.metric_source_urls())

    def test_metric_source_urls(self, mock_url_read):
        """ Test the metric source urls with one metric id. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual([], self.__report.metric_source_urls('id'))

    @patch.object(logging, 'warning')
    def test_metric_source_urls_on_error(self, mock_warning, mock_url_read):
        """ Test the metric source urls when an error occurs. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(["http://url/"], self.__report.metric_source_urls('project_1'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27project_1%27')
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Couldn't open %s: %s")
        self.assertIsInstance(mock_warning.call_args[0][2], urllib.error.HTTPError)

    def test_url(self, mock_url_read):
        """ Test the metric source base url. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual("http://url/", self.__report.url())

    def test_datetime(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.return_value = LAST_SCAN
        self.assertEqual(datetime.datetime(2017, 9, 20, 0, 43, 35), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_http_error(self, mock_url_read):
        """ Test the date and time of the report. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_missing(self, mock_url_read):
        """ Test a missing date and time of the report. """
        mock_url_read.return_value = '{"value": [{"LastScan": {}}]}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_code_unchanged(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
                                     '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
                                     'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 26, 12, 30, 24), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_code_unchanged_multiple_times(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = \
            '{"value": [{"LastScan": {"ScanCompletedOn": "2017-09-20T00:43:35.73+01:00", ' \
            '"Comment": "Attempt to perform scan on 9/26/2017 12:30:24 PM - No code changes ' \
            'were detected; Attempt to perform scan on 9/27/2017 12:30:24 PM - No code changes ' \
            'were detected; "}}]}'
        self.assertEqual(datetime.datetime(2017, 9, 27, 12, 30, 24), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_when_some_checks_have_no_date(self, mock_url_read):
        """ Test that the date and time of the report is the date and time of the last check when code is unchanged. """
        mock_url_read.return_value = \
            '{"value": [{"LastScan": {"ScanCompletedOn": "2016-12-14T00:01:30.737+01:00", ' \
            '"Comment": "Attempt to perform scan on 2/13/2017 8:00:06 PM - No code changes were ' \
            'detected;  No code changes were detected No code changes were detected"}}]}'
        self.assertEqual(datetime.datetime(2017, 2, 13, 20, 0, 6), self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_nr_warnings_on_missing_values(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(-1, self.__report.nr_warnings(['id'], 'medium'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_on_missing_values(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('id'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27id%27')

    def test_datetime_on_url_exception(self, mock_url_read):
        """ Test dealing with empty list of values. """
        mock_url_read.return_value = '{"value": []}'
        self.assertEqual(datetime.datetime.min, self.__report.datetime('raise'))
        mock_url_read.assert_called_once_with(
            'http://url/Cxwebinterface/odata/v1/Projects?$expand=LastScan&$filter=Name%20eq%20%27raise%27')
