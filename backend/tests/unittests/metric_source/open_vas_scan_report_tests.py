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

from hqlib.metric_source import OpenVASScanReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static html. """
    html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">

<html>
<body><div class="content">
<table>
<tbody><tr>
<td>Scan started:</td>
<td><b>Sun Oct 15 19:17:38 2017 UTC</b></td>
</tr>
<tr>
<td>Scan ended:</td>
<td>Sun Oct 15 19:28:58 2017 UTC</td>
</tr>
<tr>
<td>Task:</td>
<td>scan</td>
</tr>
</tbody></table>
<h2>Host Summary</h2>
<table width="100%">
<tbody><tr class="table_head">
<td>Host</td>
<td>Start</td>
<td>End</td>
<td>High</td>
<td>Medium</td>
<td>Low</td>
<td>Log</td>
<td>False Positive</td>
</tr>
<tr>
<td><a href="http://www.mediakiwi.com">test</a></td>
<td>Oct 15, 19:17:50</td>
<td>Oct 15, 19:28:58</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>18</td>
<td>0</td>
</tr>
<tr>
<td>Total: 1</td>
<td></td>
<td></td>
<td>0</td>
<td>2</td>
<td>1</td>
<td>18</td>
<td>0</td>
</tr>
</tbody></table>
<h1>Results per Host</h1>
<h2 id="test">Host test</h2>
<table>
<tbody><tr>
<td>Scanning of this host started at:</td>
<td>Sun Oct 15 19:17:50 2017 UTC</td>
</tr>
<tr>
<td>Number of results:</td>
<td>19</td>
</tr>
</tbody></table>
</body></html>'''

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib.error.HTTPError(url, None, None, None, None)
        else:
            return self.html


class OpenVASScanReportTest(unittest.TestCase):
    """ Unit tests for the open VAS Scan report class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__report = OpenVASScanReport(url_open=self.__opener.url_open)

    def test_high_risk_alerts(self):
        """ Test the number of high risk alerts. """
        self.assertEqual(0, self.__report.alerts('high', 'url'))

    def test_medium_risk_alerts(self):
        """ Test the number of medium risk alerts. """
        self.assertEqual(2, self.__report.alerts('medium', 'url'))

    def test_low_risk_alerts(self):
        """ Test the number of low risk alerts. """
        self.assertEqual(1, self.__report.alerts('low', 'url'))

    def test_passed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.alerts('high', 'raise'))

    def test_multiple_urls(self):
        """ Test the number of alerts for multiple urls. """
        self.assertEqual(4, self.__report.alerts('medium', 'url1', 'url2'))

    def test_datetime(self):
        """ Test that the date/time can be parsed. """
        self.assertEqual(datetime.datetime(2017, 10, 15, 19, 28, 58), self.__report.datetime('url'))

    def test_datetime_on_error(self):
        """ Test that the date/time is the minimum date/time when an error occurs. """
        self.assertEqual(datetime.datetime.min, self.__report.datetime('raise'))

    def test_empty_report(self):
        """ Test that the value is -1 when the report is invalid. """
        opener = FakeUrlOpener()
        opener.html = ''
        report = OpenVASScanReport(url_open=opener.url_open)
        self.assertEqual(-1, report.alerts('high', 'url'))

    def test_date_time_of_empty_report(self):
        """ Test that the date time is datetime.min when the report is invalid. """
        opener = FakeUrlOpener()
        opener.html = ''
        report = OpenVASScanReport(url_open=opener.url_open)
        self.assertEqual(datetime.datetime.min, report.datetime('url'))
