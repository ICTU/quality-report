"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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
        <tbody><tr height="24" class="risk-high">
        <th width="20%"><a name="high"></a>High (Medium)</th><th width="80%">Anti CSRF Tokens Scanner</th>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Description</td><td width="80%">Warning description</td>
        </tr>
        <tr valign="top">
        <td colspan="2"></td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent1">URL</td><td width="80%">https://test.org/gebruikersgegevens/details.jsf</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Method</td><td width="80%">GET</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Evidence</td><td width="80%">&lt;blablatest
         enctype="application/x-www-form-urlencoded"&gt;</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent1">URL</td><td width="80%">https://test.org/scripts/jquery-3.2.1.min.js</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Method</td><td width="80%">GET</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Evidence</td><td width="80%">&lt;form&gt;</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent1">URL</td><td width="80%">https://test.org/gebruikersgegevens/details2.jsf</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Method</td><td width="80%">GET</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Evidence</td><td width="80%">&lt;test12321412
         enctype="application/x-www-form-urlencoded"&gt;</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Instances</td><td width="80%">2</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Solution</td><td width="80%"><p>Phase: Architecture and Design</p><p>Use a vetted
         library or framework that does not allow this weakness to occur or provides constructs that make
         this weakness easier to avoid.</p><p>For example, use anti-CSRF packages such as the OWASP CSRFGuard.</p>
        <p></p><p>Phase: Implementation</p><p>Ensure that your application is free of cross-site scripting issues,
         because most CSRF defenses can be bypassed using attacker-controlled script.</p><p></p><p>Phase: Architecture
         and Design</p><p>Generate a unique nonce for each form, place the nonce into the form, and verify the nonce
         upon receipt of the form. Be sure that the nonce is not predictable (CWE-330).</p><p>Note that this can be
         bypassed using XSS.</p><p></p><p>Identify especially dangerous operations. When the user performs a dangerous
         operation, send a separate confirmation request to ensure that the user intended to perform that operation.
        </p><p>Note that this can be bypassed using XSS.</p><p></p><p>Use the ESAPI Session Management control.</p>
        <p>This control includes a component for CSRF.</p><p></p><p>Do not use the GET method for any request that
         triggers a state change.</p><p></p><p>Phase: Implementation</p><p>Check the HTTP Referer header to see if
         the request originated from an expected page. This could break legitimate functionality, because users or
         proxies may have disabled sending the Referer for privacy reasons.</p></td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Reference</td><td width="80%"><p>http://projects.webappsec.org/Cross-Site-Request-Forgery</p>
        <p>http://cwe.mitre.org/data/definitions/352.html</p></td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">CWE Id</td><td width="80%">352</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">WASC Id</td><td width="80%">9</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Source ID</td><td width="80%">1</td>
        </tr>
        </tbody></table>
        <table width="100%" class="results">
        <tr height="24" class="risk-medium">
        <th width="20%"><a name="medium"></a>Medium (Medium)</th><th width="80%">X-Frame-Options Header Not Set</th>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Description</td><td width="80%"><p>X-Frame-Options header is not included in the HTTP
         response to protect against 'ClickJacking' attacks.</p></td>
        </tr>
        <TR vAlign="top">
        <TD colspan="2"></TD>
        </TR>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent1">URL</td><td width="80%">http://xxxx.org/test.jsf</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Method</td><td width="80%">GET</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%" class="indent2">Parameter</td><td width="80%">X-Frame-Options</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Instances</td><td width="80%">1</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Solution</td><td width="80%"><p>Most modern Web browsers support the X-Frame-Options HTTP
         header. Ensure it's set on all web pages returned by your site (if you expect the page to be framed only
         by pages on your server (e.g. it's part of a FRAMESET) then you'll want to use SAMEORIGIN, otherwise if
         you never expect the page to be framed, you should use DENY. ALLOW-FROM allows specific websites to frame
         the web page in supported web browsers).</p></td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Reference</td><td width="80%"><p>
        http://blogs.msdn.com/b/ieinternals/archive/2010/03/30/combating-clickjacking-with-x-frame-options.aspx
        </p></td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">CWE Id</td><td width="80%">16</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">WASC Id</td><td width="80%">15</td>
        </tr>
        <tr bgcolor="#e8e8e8">
        <td width="20%">Source ID</td><td width="80%">3</td>
        </tr>
        </table>
    </body>
    </html>
    '''

FALSE_POSITIVE_SUCCESS = '''{"a19fee1fb9fe0ecf8102af6d60d74d01":{"reason": "test123"},
    "7bc4004792cdb03dd775646c94088c50":{"reason": "test456"}}'''
FALSE_POSITIVE_ERROR = '{xxxx}'


@patch.object(url_opener.UrlOpener, 'url_read')
class ZAPScanReportTest(unittest.TestCase):
    """ Unit tests for the ZAP Scan report class. """

    def setUp(self):
        ZAPScanReport.alerts.cache_clear()
        # pylint: disable=protected-access
        ZAPScanReport._ZAPScanReport__get_soup.cache_clear()
        self.__report = ZAPScanReport('')

    def test_get_warnings_info(self, mock_url_read):
        """ Test that data about warnings are extracted correctly. """
        mock_url_read.return_value = ZAP_REPORT
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([("Anti CSRF Tokens Scanner",
                           "https://test.org/gebruikersgegevens/details.jsf",
                           "Not available"),
                          ("Anti CSRF Tokens Scanner",
                           "https://test.org/scripts/jquery-3.2.1.min.js",
                           "Not available"),
                          ("Anti CSRF Tokens Scanner",
                           "https://test.org/gebruikersgegevens/details2.jsf",
                           "Not available")], result)

    def test_get_warnings_info_false_postive_api(self, mock_url_read):
        """ Test that data about warnings and false positives are extracted correctly. """
        mock_url_read.return_value = FALSE_POSITIVE_SUCCESS
        self.__report = ZAPScanReport('http://127.0.0.1/')

        mock_url_read.return_value = ZAP_REPORT
        result = self.__report.get_warnings_info('high', 'url')
        self.assertEqual([("Anti CSRF Tokens Scanner",
                           "https://test.org/gebruikersgegevens/details.jsf",
                           ('a19fee1fb9fe0ecf8102af6d60d74d01',
                            True, "test123", 'http://127.0.0.1/')),
                          ("Anti CSRF Tokens Scanner",
                           "https://test.org/scripts/jquery-3.2.1.min.js",
                           ('7bc4004792cdb03dd775646c94088c50',
                            True, "test456", 'http://127.0.0.1/')),
                          ("Anti CSRF Tokens Scanner",
                           "https://test.org/gebruikersgegevens/details2.jsf",
                           ('8259ec1afddcb6f792e442b331a782c6',
                            False, "", 'http://127.0.0.1/'))], result)
        self.__report = ZAPScanReport('')

    def test_get_false_positives_http_error(self, mock_url_read):
        """ Test that the false positive list is empty when http error happens. """
        mock_url_read.side_effect = urllib.error.HTTPError('raise', None, None, None, None)
        self.__report = ZAPScanReport('http://127.0.0.1/')
        self.assertEqual([], self.__report.false_positives_list)
        self.__report = ZAPScanReport('')

    def test_get_false_positives_key_error(self, mock_url_read):
        """ Test that the false positive list is empty when json error happens. """
        mock_url_read.return_value = FALSE_POSITIVE_ERROR
        self.__report = ZAPScanReport('http://127.0.0.1/')
        self.assertEqual([], self.__report.false_positives_list)
        self.__report = ZAPScanReport('')

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

    def test_high_risk_alerts_false_postive_api(self, mock_url_read):
        """ Test the number of high alerts with false positives are ignored correctly. """
        mock_url_read.return_value = FALSE_POSITIVE_SUCCESS
        self.__report = ZAPScanReport('http://127.0.0.1/')

        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(1, self.__report.alerts('high', 'url'))
        self.__report = ZAPScanReport('')

    def test_high_risk_alerts(self, mock_url_read):
        """ Test the number of high risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(3, self.__report.alerts('high', 'url'))
        mock_url_read.assert_called_once()

    def test_medium_risk_alerts(self, mock_url_read):
        """ Test the number of medium risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(1, self.__report.alerts('medium', 'url'))
        mock_url_read.assert_called_once()

    def test_low_risk_alerts(self, mock_url_read):
        """ Test the number of low risk alerts. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(0, self.__report.alerts('low', 'url'))
        mock_url_read.assert_called_once()

    def test_multiple_urls(self, mock_url_read):
        """ Test the number of alerts for multiple urls. """
        mock_url_read.return_value = ZAP_REPORT
        self.assertEqual(2, self.__report.alerts('medium', 'url1', 'url2'))
        self.assertEqual(mock_url_read.call_args_list, [call('url1'), call('url2')])

    def test_missing_table(self, mock_url_read):
        """ Test that a missing table can be handled. """
        mock_url_read.return_value = '<html></html>'
        self.assertEqual(0, self.__report.alerts('high', 'url'))
        mock_url_read.assert_called_once()
