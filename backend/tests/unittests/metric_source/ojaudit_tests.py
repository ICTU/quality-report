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

import unittest
from unittest.mock import patch

from hqlib.metric_source import url_opener, OJAuditReport


class OJAuditReportTest(unittest.TestCase):
    """ Unit tests for the OJAudit report class. """

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_violations(self, mock_url_read):
        """ Test the number of violations. """
        mock_url_read.return_value = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <warning-count>2</warning-count></audit>"""
        self.assertEqual(2, OJAuditReport().violations("warning", "http://ojaudit/report.xml"))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_violations_conn_error(self, mock_url_read):
        """ Test that the number of violations is -1 on a connection error. """
        mock_url_read.side_effect = url_opener.UrlOpener.url_open_exceptions[0](None, None, None, None, None)
        self.assertEqual(-1, OJAuditReport().violations("warning", "http://ojaudit/report.xml"))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_violations_parse_error(self, mock_url_read):
        """ Test that the number of violations is -1 on a connection error. """
        mock_url_read.return_value = '<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit"><warning-count>2'
        self.assertEqual(-1, OJAuditReport().violations("warning", "http://ojaudit/report.xml"))

    def test_metric_source_url(self):
        """Test that the url to the human-readable version of the report is returned."""
        self.assertEqual(["http://ojaudit/report.html"],
                         OJAuditReport().metric_source_urls("http://ojaudit/report.xml"))
