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

import logging
import datetime
import unittest
from unittest.mock import patch
import urllib.error

from hqlib.metric_source import LCOV, url_opener


HTML = '''<table><tr><td><table><tr>
            <td class="headerItem">{header}</td>
            <td class="headerCovTableEntry">{hit}</td>
            <td class="headerCovTableEntry">{total}</td>
          </tr></table></td></tr></table>'''


@patch.object(url_opener.UrlOpener, 'url_read')
class LCOVTest(unittest.TestCase):
    """ Unit tests for the LCOV class. """

    def setUp(self):
        # pylint: disable=no-member
        # pylint: disable=protected-access
        LCOV._HTMLCoverageReport__get_soup.cache_clear()
        LCOV._LCOV__get_report_tds.cache_clear()
        LCOV.datetime.cache_clear()
        self.__lcov = LCOV()

    def test_statement_coverage(self, mock_url_read):
        """ Test the statement coverage. """
        mock_url_read.return_value = HTML.format(header='Lines:', hit=20, total=22)
        self.assertAlmostEqual(90.91, self.__lcov.statement_coverage('http://lcov'), places=2)

    def test_statement_coverage_onerror(self, mock_url_read):
        """ Test that the reported statement coverage is -1 when LCOV can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(-1, self.__lcov.statement_coverage('raise'))

    @patch.object(logging, 'error')
    def test_statement_coverage_no_header(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 when header can't be found in the report. """
        mock_url_read.return_value = HTML.format(header='Bugs:', hit=20, total=22)
        self.assertEqual(-1, self.__lcov.statement_coverage('http://lcov'))
        mock_error.assert_called_once_with('Header %s is not found in the report.', 'Lines')

    @patch.object(logging, 'error')
    def test_statement_coverage_empty_table(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 when html table of the report is empty. """
        mock_url_read.return_value = '''<table><table></table></table>'''
        self.assertEqual(-1, self.__lcov.statement_coverage('http://lcov'))
        mock_error.assert_called_once_with('Header %s is not found in the report.', 'Lines')

    @patch.object(logging, 'error')
    def test_statement_invalid_number(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 and logs when invalid number is found. """
        mock_url_read.return_value = HTML.format(header='Lines:', hit='', total=22)
        self.assertEqual(-1, self.__lcov.statement_coverage('http://lcov'))
        mock_error.assert_called()
        self.assertEqual(mock_error.call_args[0][0], "Error calculating coverage percentage for %s. Reason: %s")
        self.assertEqual(mock_error.call_args[0][1], 'Lines')
        self.assertIsInstance(mock_error.call_args[0][2], ValueError)

    @patch.object(logging, 'error')
    def test_statement_bad_html(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 and logs when bad html is found. """
        mock_url_read.return_value = 'no html at all!'
        self.assertEqual(-1, self.__lcov.statement_coverage('http://lcov'))
        mock_error.assert_called()
        self.assertEqual(mock_error.call_args[0][0], "Error parsing html. Reason: %s")
        self.assertIsInstance(mock_error.call_args[0][1], AttributeError)

    @patch.object(logging, 'error')
    def test_statement_zero_total_lines(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 when header can't be found in the report. """
        mock_url_read.return_value = HTML.format(header='Lines:', hit=20, total=0)
        self.assertEqual(-1, self.__lcov.statement_coverage('http://lcov'))
        mock_error.assert_called_once_with('Total reported number of %s is found to be zero!', 'Lines')

    def test_branch_coverage(self, mock_url_read):
        """ Test the branch coverage. """
        mock_url_read.return_value = HTML.format(header='Branches:', hit=20, total=22)
        self.assertAlmostEqual(90.91, self.__lcov.branch_coverage('http://lcov'), places=2)

    def test_coverage_date(self, mock_url_read):
        """ Test the date of the coverage report. """
        mock_url_read.return_value = HTML.format(header='Date:', hit='2016-12-20 14:12:28', total='unimportant')
        expected = datetime.datetime(2016, 12, 20, 14, 12, 28)
        self.assertEqual(expected, self.__lcov.datetime('http://lcov'))

    def test_coverage_date_on_error(self, mock_url_read):
        """ Test that the date is now when LCOV can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__lcov.datetime('http://lcov'))

    @patch.object(logging, 'error')
    def test_coverage_date_bad_html(self, mock_error, mock_url_read):
        """ Test that the date is now when LCOV html is bogus. """
        mock_url_read.side_effect = 'no html at all!'
        self.assertEqual(datetime.datetime.min, self.__lcov.datetime('http://lcov'))
        self.assertEqual(mock_error.call_args[0][0], "Error parsing html. Reason: %s")
        self.assertIsInstance(mock_error.call_args[0][1], AttributeError)

    @patch.object(logging, 'error')
    def test_coverage_date_bad_date(self, mock_error, mock_url_read):
        """ Test that the statement coverage is -1 and logs when invalid number is found. """
        mock_url_read.return_value = HTML.format(header='Date:', hit='2016-99-20 14:12:28', total='unimportant')
        self.assertEqual(datetime.datetime.min, self.__lcov.datetime('http://lcov'))
        mock_error.assert_called()
        self.assertEqual(mock_error.call_args[0][0], "Error parsing report for %s. Reason: %s")
        self.assertEqual(mock_error.call_args[0][1], 'Date')
        self.assertIsInstance(mock_error.call_args[0][2], ValueError)

    @patch.object(logging, 'error')
    def test_coverage_coverage_no_header(self, mock_error, mock_url_read):
        """ Test that the report date is now when header can't be found in the report. """
        mock_url_read.return_value = HTML.format(header='Bugs:', hit='2016-12-20 14:12:28', total=22)
        self.assertEqual(datetime.datetime.min, self.__lcov.datetime('http://lcov'))
        mock_error.assert_called_once_with('Header %s is not found in the report.', 'Date')
