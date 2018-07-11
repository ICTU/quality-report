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
