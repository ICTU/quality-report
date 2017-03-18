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

from hqlib.metric_source import ZAPScanReport


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Fake the url opener to return static html. """
    html = '''<html>
<body>
<table width="45%" border="0">
<tr bgcolor="#666666">
<td width="45%" height="24"><strong><font color="#FFFFFF" size="2" face="Arial, Helvetica, sans-serif">Risk
      Level</font></strong></td><td width="55%" align="center"><strong><font color="#FFFFFF" size="2"
      face="Arial, Helvetica, sans-serif">Number of Alerts</font></strong></td>
</tr>
<tr bgcolor="#e8e8e8">
<td><font size="2" face="Arial, Helvetica, sans-serif"><a href="#high">High</a></font></td>
<td align="center"><font size="2" face="Arial, Helvetica, sans-serif">0</font></td>
</tr>
<tr bgcolor="#e8e8e8">
<td><font size="2" face="Arial, Helvetica, sans-serif"><a href="#medium">Medium</a></font></td>
<td align="center"><font size="2" face="Arial, Helvetica, sans-serif">1</font></td>
</tr>
<tr bgcolor="#e8e8e8">
<td><font size="2" face="Arial, Helvetica, sans-serif"><a href="#low">Low</a></font></td>
<td align="center"><font size="2" face="Arial, Helvetica, sans-serif">4</font></td>
</tr>
<tr bgcolor="#e8e8e8">
<td><font size="2" face="Arial, Helvetica, sans-serif"><a href="#info">Informational</a></font></td>
<td align="center"><font size="2" face="Arial, Helvetica, sans-serif">2</font></td>
</tr>
</table>
</body>
</html>
'''

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib.error.HTTPError(url, None, None, None, None)
        else:
            return self.html


class ZAPScanReportTest(unittest.TestCase):
    """ Unit tests for the ZAP Scan report class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        ZAPScanReport.alerts.cache_clear()
        ZAPScanReport._ZAPScanReport__get_soup.cache_clear()
        self.__report = ZAPScanReport(url_open=self.__opener.url_open)

    def test_high_risk_alerts(self):
        """ Test the number of high risk alerts. """
        self.assertEqual(0, self.__report.alerts('high', 'url'))

    def test_medium_risk_alerts(self):
        """ Test the number of medium risk alerts. """
        self.assertEqual(1, self.__report.alerts('medium', 'url'))

    def test_low_risk_alerts(self):
        """ Test the number of low risk alerts. """
        self.assertEqual(4, self.__report.alerts('low', 'url'))

    def test_passed_raise(self):
        """ Test that the value is -1 when the report can't be opened. """
        self.assertEqual(-1, self.__report.alerts('high', 'raise'))

    def test_multiple_urls(self):
        """ Test the number of alerts for multiple urls. """
        self.assertEqual(2, self.__report.alerts('medium', 'url1', 'url2'))

    def test_missing_table(self):
        """ Test that a missing table can be handled. """
        self.__opener.html = '<html></html>'
        self.assertEqual(-1, self.__report.alerts('high', 'url'))
