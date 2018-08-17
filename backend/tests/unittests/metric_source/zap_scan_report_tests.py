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

import traceback
import logging
import unittest
from unittest.mock import patch, call

import urllib.error
from hqlib.metric_source import ZAPScanReport, url_opener

ZAP_REPORT = '''<html>
    <body>
    <table width="45%" class="summary">
    <tr bgcolor="#666666">
    <th width="45%" height="24">Risk
          Level</th><th width="55%" align="center">Number
          of Alerts</th>
    </tr>
    <tr bgcolor="#e8e8e8">
    <td><a href="#high">High</a></td><td align="center">0</td>
    </tr>
    <tr bgcolor="#e8e8e8">
    <td><a href="#medium">Medium</a></td><td align="center">1</td>
    </tr>
    <tr bgcolor="#e8e8e8">
    <td><a href="#low">Low</a></td><td align="center">4</td>
    </tr>
    <tr bgcolor="#e8e8e8">
    <td><a href="#info">Informational</a></td><td align="center">1</td>
    </tr>
    </table>
    <div class="spacer-lg"></div>
    <h3>Alert Detail</h3>
    <div class="spacer"></div>
    <table width="100%" class="results">
        <tr height="24" class="risk-high">
            <th width="20%"><a name="high"></a>High (Medium)</th>
            <th width="80%">Warning Name</th>
        </tr>
        <tr bgcolor="#e8e8e8">
            <td width="20%">Description</td>
            <td width="80%">{description}</td>
        </tr>
    </table>
    </body>
    </html>
    '''


@patch.object(url_opener.UrlOpener, 'url_read')
class ZAPScanReportTest(unittest.TestCase):
    """ Unit tests for the ZAP Scan report class. """

    def setUp(self):
        ZAPScanReport.alerts.cache_clear()
        ZAPScanReport._ZAPScanReport__get_soup.cache_clear()
        self.__report = ZAPScanReport()

    def test_get_warnings_info(self, mock_url_read):
        """ Test that data about warnings are extracted correctly. """
        mock_url_read.return_value = ZAP_REPORT.format(description="Be aware!")
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([("Warning Name", "Be aware!")], result)

    def test_get_warnings_info_with_broad_description(self, mock_url_read):
        """ Test that data about warnings are extracted correctly, when the description is folded in sub-elements. """
        mock_url_read.return_value = ZAP_REPORT.format(
            description="<div><p>The First Part</p><span>of a very long description</span></div>"
        )
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([("Warning Name", "The First Part")], result)

    def test_get_warnings_info_http_error(self, mock_url_read):
        """ Test that data about warnings are empty when http error happens. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([], result)

    @patch.object(logging, 'warning')
    def test_get_warnings_info_attribute_error(self, mock_warning, mock_url_read):
        """ Test that data about warnings are empty and appropriate logging is done no expected html tags are found. """
        mock_url_read.return_value = 'no table at all!'
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([], result)
        mock_warning.assert_called_once_with("Couldn't find any entries with %s risk level.", "high")

    @patch.object(traceback, 'print_exc')
    @patch.object(logging, 'warning')
    def test_get_warnings_info_index_error(self, mock_warning, mock_traceback, mock_url_read):
        """ Test that data about warnings are empty and appropriate logging is done no expected html tags are found. """
        mock_url_read.return_value = '<table class="results"><tr class="risk-high"><th /></tr></table> '
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([], result)
        mock_warning.assert_called_once()
        self.assertEqual(mock_warning.call_args[0][0], "Couldn't parse alert details with %s risk level from %s: %s")
        self.assertEqual(mock_warning.call_args[0][1], 'high')
        self.assertEqual(mock_warning.call_args[0][2], 'url')
        self.assertIsInstance(mock_warning.call_args[0][3], IndexError)
        mock_traceback.assert_called_once()

    def test_high_risk_alerts(self, mock_url_read):
        """ Test the number of high risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(0, self.__report.alerts('high', 'url'))
        mock_url_read.assert_called_once()

    def test_medium_risk_alerts(self, mock_url_read):
        """ Test the number of medium risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(1, self.__report.alerts('medium', 'url'))
        mock_url_read.assert_called_once()

    def test_low_risk_alerts(self, mock_url_read):
        """ Test the number of low risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(4, self.__report.alerts('low', 'url'))
        mock_url_read.assert_called_once()

    def test_passed_raise(self, mock_url_read):
        """ Test that the value is -1 when the report can't be opened. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.assertEqual(-1, self.__report.alerts('high', 'raise'))
        mock_url_read.assert_called_once()

    def test_multiple_urls(self, mock_url_read):
        """ Test the number of alerts for multiple urls. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(2, self.__report.alerts('medium', 'url1', 'url2'))
        self.assertEqual(mock_url_read.call_args_list, [call('url1'), call('url2')])

    def test_missing_table(self, mock_url_read):
        """ Test that a missing table can be handled. """
        mock_url_read.return_value = '<html></html>'
        self.assertEqual(-1, self.__report.alerts('high', 'url'))
        mock_url_read.assert_called_once()
