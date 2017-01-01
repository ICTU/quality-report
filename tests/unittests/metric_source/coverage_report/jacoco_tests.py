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

import datetime
import unittest
import urllib2

from hqlib.metric_source import JaCoCo


class FakeUrlOpener(object):  # pylint: disable=too-few-public-methods
    """ Return fixed data for test purposes. """
    html = '<tfoot><tr><td>Total</td><td class="bar">1,162 of 6,293</td>' \
        '<td class="ctr2">82%</td><td class="bar">161 of 422</td>' \
        '<td class="ctr2">62%</td><td class="ctr1">287</td>' \
        '<td class="ctr2">807</td><td class="ctr1">297</td>' \
        '<td class="ctr2">1,577</td><td class="ctr1">138</td>' \
        '<td class="ctr2">592</td><td class="ctr1">12</td>' \
        '<td class="ctr2">79</td></tr></tfoot>'
    date_html = '<tbody><tr><td><span class="el_session">na-node1-reg-' \
        '1196e1b5</span></td><td>Apr 4, 2013 4:41:29 PM</td><td>Apr 5, 2013 ' \
        '10:34:54 AM</td></tr><tr><td><span class="el_session">na-node2-reg-' \
        '1f82fbab</span></td><td>Apr 4, 2013 4:43:39 PM</td><td>Apr 5, 2013 ' \
        '10:34:55 AM</td></tr></tbody>'

    def url_open(self, url):
        """ Open a url. """
        if 'raise' in url:
            raise urllib2.HTTPError(url, None, None, None, None)
        else:
            html = self.html if url.endswith('index.html') else self.date_html
            return html


class JacocoTest(unittest.TestCase):
    """ Unit tests for the Jacoco class. """

    def setUp(self):
        self.__opener = FakeUrlOpener()
        self.__jacoco = JaCoCo(url_open=self.__opener.url_open)

    def test_statement_coverage(self):
        """ Test the statement coverage for a specific product. """
        self.assertEqual(round(100 * (6293 - 1162) / 6293.),
                         self.__jacoco.statement_coverage('http://jacoco/index.html'))

    def test_zero_statement_coverage(self):
        """ Test zero statement coverage. """
        self.__opener.html = '<tfoot><tr>' \
            '<td>Total</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td></tr></tfoot>'
        self.assertEqual(0, self.__jacoco.statement_coverage('http://jacoco/index.html'))

    def test_statement_coverage_on_error(self):
        """ Test that the reported statement coverage is -1 when Jacoco can't be reached. """
        self.assertEqual(-1, self.__jacoco.statement_coverage('raise'))

    def test_statement_coverage_on_parse_error(self):
        """ Test that the reported statement coverage is -1 when the Jacoco output can't be parsed. """
        self.__opener.html = '<tfoot><tr></tr></tfoot>'
        self.assertRaises(IndexError, self.__jacoco.statement_coverage, 'http://jacoco/index.html')

    def test_branch_coverage(self):
        """ Test the branch coverage for a specific product. """
        self.assertEqual(round(100 * (422 - 161) / 422.), self.__jacoco.branch_coverage('http://jacoco/index.html'))

    def test_zero_branch_coverage(self):
        """ Test zero branch coverage. """
        self.__opener.html = '<tfoot><tr>' \
            '<td>Total</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="bar">0 of 0</td>' \
            '<td class="ctr2">0%</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td><td class="ctr1">0</td>' \
            '<td class="ctr2">0</td></tr></tfoot>'
        self.assertEqual(0, self.__jacoco.branch_coverage('http://jacoco/index.html'))

    def test_branch_coverage_on_error(self):
        """ Test that the reported branch coverage is -1 when Jacoco can't be reached. """
        self.assertEqual(-1, self.__jacoco.branch_coverage('raise'))

    def test_coverage_date(self):
        """ Test the date of the coverage report. """
        expected = datetime.datetime(2013, 4, 5, 10, 34, 55)
        self.assertEqual(expected, self.__jacoco.coverage_date('http://jacoco'))

    def test_coverage_date_non_us(self):
        """ Test the date of the coverage report when it's not a US date/time. """
        self.__opener.date_html = '<tbody><tr><td><span class="el_session">na-node1-reg-' \
            '1196e1b5</span></td><td>4-apr-2013 16:41:29</td><td>5-apr-2013 ' \
            '10:34:54</td></tr><tr><td><span class="el_session">na-node2-reg-' \
            '1f82fbab</span></td><td>4-apr-2013 16:43:39</td><td>5-apr-2013 ' \
            '10:34:55</td></tr></tbody>'
        expected = datetime.datetime(2013, 4, 5, 10, 34, 55)
        self.assertEqual(expected, self.__jacoco.coverage_date('http://jacoco'))

    def test_coverage_date_on_error(self):
        """ Test that the date is now when JaCoCo can't be reached. """
        coverage_date = self.__jacoco.coverage_date('raise/index.html')
        age = datetime.datetime.now() - coverage_date
        self.assertTrue(age < datetime.timedelta(seconds=1))

    def test_coverage_date_url(self):
        """ Test that the coverage date url is different than the coverage url for JaCoCo. """
        # pylint: disable=protected-access
        self.assertEqual('coverage_report/.sessions.html',
                         self.__jacoco._get_coverage_date_url('coverage_report/index.html'))
