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
from unittest.mock import patch
import urllib.error

from hqlib.metric_source import JaCoCo, url_opener


HTML = '<tfoot><tr><td>Total</td><td class="bar">1,162 of 6,293</td>' \
    '<td class="ctr2">82%</td><td class="bar">161 of 422</td>' \
    '<td class="ctr2">62%</td><td class="ctr1">287</td>' \
    '<td class="ctr2">807</td><td class="ctr1">297</td>' \
    '<td class="ctr2">1,577</td><td class="ctr1">138</td>' \
    '<td class="ctr2">592</td><td class="ctr1">12</td>' \
    '<td class="ctr2">79</td></tr></tfoot>'
DATE_HTML = '<tbody><tr><td><span class="el_session">na-node1-reg-' \
    '1196e1b5</span></td><td>Apr 4, 2013 4:41:29 PM</td><td>Apr 5, 2013 ' \
    '10:34:54 AM</td></tr><tr><td><span class="el_session">na-node2-reg-' \
    '1f82fbab</span></td><td>Apr 4, 2013 4:43:39 PM</td><td>Apr 5, 2013 ' \
    '10:34:55 AM</td></tr></tbody>'


@patch.object(url_opener.UrlOpener, 'url_read')
class JacocoTest(unittest.TestCase):
    """ Unit tests for the Jacoco class. """

    def setUp(self):
        JaCoCo._HTMLCoverageReport__get_soup.cache_clear()
        self.__jacoco = JaCoCo()

    def test_statement_coverage(self, mock_url_read):
        """ Test the statement coverage for a specific product. """
        mock_url_read.return_value = HTML
        self.assertAlmostEqual(100 * (6293 - 1162) / 6293.,
                               self.__jacoco.statement_coverage('http://jacoco/index.html'))

    def test_has_branch_coverage(self, mock_url_read):
        """ Test that coverage report has branch coverage. """
        mock_url_read.return_value = 'dummy'
        self.assertTrue(self.__jacoco.has_branch_coverage('dummy'))

    def test_zero_statement_coverage(self, mock_url_read):
        """ Test zero statement coverage. """
        mock_url_read.return_value = '<tfoot><tr>' \
            '<td>Total</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td></tr></tfoot>'
        self.assertEqual(0, self.__jacoco.statement_coverage('http://jacoco/index.html'))

    def test_statement_coverage_onerror(self, mock_url_read):
        """ Test that the reported statement coverage is -1 when Jacoco can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(-1, self.__jacoco.statement_coverage('raise'))

    def test_statement_coverage_parse(self, mock_url_read):
        """ Test that the reported statement coverage is -1 when the Jacoco output can't be parsed. """
        mock_url_read.return_value = '<tfoot><tr></tr></tfoot>'
        self.assertRaises(IndexError, self.__jacoco.statement_coverage, 'http://jacoco/index.html')

    def test_branch_coverage(self, mock_url_read):
        """ Test the branch coverage for a specific product. """
        mock_url_read.return_value = HTML
        self.assertAlmostEqual(100 * (422 - 161) / 422., self.__jacoco.branch_coverage('http://jacoco/index.html'))

    def test_zero_branch_coverage(self, mock_url_read):
        """ Test zero branch coverage. """
        mock_url_read.return_value = '<tfoot><tr>' \
            '<td>Total</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td></tr></tfoot>'
        self.assertEqual(0, self.__jacoco.branch_coverage('http://jacoco/index.html'))

    def test_branch_coverage_on_error(self, mock_url_read):
        """ Test that the reported branch coverage is -1 when Jacoco can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(-1, self.__jacoco.branch_coverage('raise'))

    def test_coverage_date(self, mock_url_read):
        """ Test the date of the coverage report. """
        mock_url_read.return_value = DATE_HTML
        self.assertEqual(datetime.datetime(2013, 4, 5, 10, 34, 55), self.__jacoco.datetime('http://jacoco'))

    def test_coverage_date_non_us(self, mock_url_read):
        """ Test the date of the coverage report when it's not a US date/time. """
        mock_url_read.return_value = '<tbody><tr><td><span class="el_session">na-node1-reg-' \
            '1196e1b5</span></td><td>4-apr-2013 16:41:29</td><td>5-apr-2013 ' \
            '10:34:54</td></tr><tr><td><span class="el_session">na-node2-reg-' \
            '1f82fbab</span></td><td>4-apr-2013 16:43:39</td><td>5-apr-2013 ' \
            '10:34:55</td></tr></tbody>'
        self.assertEqual(datetime.datetime(2013, 4, 5, 10, 34, 55), self.__jacoco.datetime('http://jacoco'))

    def test_coverage_date_on_error(self, mock_url_read):
        """ Test that the date is the minimum date when JaCoCo can't be reached. """
        mock_url_read.side_effect = urllib.error.HTTPError('', None, None, None, None)
        self.assertEqual(datetime.datetime.min, self.__jacoco.datetime('raise/index.html'))

    def test_coverage_date_url(self, mock_url_read):
        """ Test that the coverage date url is different than the coverage url for JaCoCo. """
        # pylint: disable=protected-access
        mock_url_read.return_value = DATE_HTML
        self.assertEqual(['coverage_report/jacoco-sessions.html', 'coverage_report/.sessions.html'],
                         self.__jacoco._get_coverage_date_urls('coverage_report/index.html'))
