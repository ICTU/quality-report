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
import urllib2

from hqlib.metric_source import OpenVASScanReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static html. """
    html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<body><div><table><tr><td valign="top">
<h1>Summary</h1>
<table>
<tr>
<td>Scan started:</td>
<td><b>Mon Aug 8 12:31:31 2016 UTC</b></td>
</tr>
<tr>
<td>Scan ended:</td>
<td>Mon Aug 8 12:37:04 2016 UTC</td>
</tr>
<tr>
<td>Task:</td>
<td>openvas_lib_scan_www.mediawiki.dep.org</td>
</tr>
</table>
<h2>Host Summary</h2>
<table>
<tr style="background-color: #d5d5d5;">
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
<td><a href="#22.33.44.55">22.33.44.55 (www.mediawiki.dep.org)</a></td>
<td>Aug 8, 12:31:36</td>
<td>Aug 8, 12:37:04</td>
<td>0</td>
<td>2</td>
<td>1</td>
<td>13</td>
<td>0</td>
</tr>
<tr>
<td>Total: 1</td>
<td></td>
<td></td>
<td>0</td>
<td>2</td>
<td>1</td>
<td>13</td>
<td>0</td>
</tr>
</table>
</div>
</body>
</html>
'''

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
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
