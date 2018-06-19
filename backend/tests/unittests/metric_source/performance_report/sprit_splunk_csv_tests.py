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
import io
import pathlib
import unittest
import urllib.error
from typing import IO

from hqlib.metric_source import SpiritSplunkCSVPerformanceLoadTestReport


CSV = (pathlib.Path(__file__).resolve().parent / "spirit_splunk_csv.txt").read_bytes()


class ReportUnderTest(SpiritSplunkCSVPerformanceLoadTestReport):  # pylint: disable=too-few-public-methods
    """ Override the performance report to return the url as report contents. """

    def url_open(self, url: str, log_error: bool = True) -> IO:  # pylint: disable=no-self-use,unused-argument
        """ Return the static html. """
        if 'error' in url:
            raise urllib.error.URLError('reason')
        else:
            return io.BytesIO(CSV)


class SpiritSplunkCSVPerformanceReportTest(unittest.TestCase):
    """ Unit tests for the Spirit Splunk CSV performance report metric source. """
    expected_queries = 22
    expected_queries_violating_max_responsetime = 17

    def setUp(self):
        ReportUnderTest.queries.cache_clear()
        self._performance_report = ReportUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self._performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self._performance_report.queries('product'))

    def test_queries(self):
        """ Test the total number of queries for a product/version that is in the report. """
        self.assertEqual(self.expected_queries, self._performance_report.queries('ABC'))

    def test_queries_re(self):
        """ Test that the total number of queries for a product/version that is in the report can be found using a
            regular expression. """
        self.assertEqual(self.expected_queries, self._performance_report.queries('AB.*'))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(self.expected_queries_violating_max_responsetime,
                         self._performance_report.queries_violating_max_responsetime('ABC'))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(self.expected_queries_violating_max_responsetime,
                         self._performance_report.queries_violating_wished_responsetime('ABC'))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2017, 6, 12), self._performance_report.datetime('ABC'))

    def test_date_without_urls(self):
        """ Test that the min date is passed if there are no report urls to consult. """
        class SpiritSplunkCSVReportWithoutUrls(ReportUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.datetime.min,
                         SpiritSplunkCSVReportWithoutUrls('http://report').datetime('ABC'))


class SpiritSplunkCSVPerformanceReportMultipleReportsTest(SpiritSplunkCSVPerformanceReportTest):
    """ Unit tests for a performance report metric source with multiple reports. """

    expected_queries = 2 * SpiritSplunkCSVPerformanceReportTest.expected_queries
    expected_queries_violating_max_responsetime = \
        2 * SpiritSplunkCSVPerformanceReportTest.expected_queries_violating_max_responsetime

    def setUp(self):
        self._performance_report = ReportUnderTest('http://report/',
                                                   report_urls=['http://report/1', 'http://report/2'])


class SpiritSplunkCSVPerformanceReportMissingTest(unittest.TestCase):
    """ Unit tests for a missing performance report metric source. """

    def test_queries_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries('p1'))

    def test_queries_max_responsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries_violating_max_responsetime('p2'))

    def test_queries_wished_reponsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, ReportUnderTest('http://error/').queries_violating_wished_responsetime('p3'))

    def test_date_with_missing_report(self):
        """ Test that the date of a missing report is the min date. """
        self.assertEqual(datetime.datetime.min, ReportUnderTest('http://error/').datetime('p4'))
