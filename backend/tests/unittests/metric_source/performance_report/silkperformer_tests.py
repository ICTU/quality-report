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
import os
import unittest
import urllib.error
from typing import cast, IO

from hqlib.metric_source import SilkPerformerPerformanceLoadTestReport


HTML = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "silkperformer.html"), "r").read()


class SilkPerformerUnderTest(SilkPerformerPerformanceLoadTestReport):  # pylint: disable=too-few-public-methods
    """ Override the Silk Performer performance report to return the url as report contents. """

    def url_open(self, url: str, log_error: bool = True) -> IO:  # pylint: disable=no-self-use,unused-argument
        """ Return the static html. """
        if 'error' in url:
            raise urllib.error.URLError('reason')
        return cast(IO, io.StringIO("" if "invalid" in url else HTML))


class SilkPerformerTest(unittest.TestCase):
    """ Unit tests for the Silk Performer performance report metric source. """
    expected_queries = 17

    def setUp(self):
        SilkPerformerUnderTest.queries.cache_clear()
        self._performance_report = SilkPerformerUnderTest('http://report/')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://report/', self._performance_report.url())

    def test_queries_non_existing(self):
        """ Test that the number of queries for a product/version that is not found is zero. """
        self.assertEqual(0, self._performance_report.queries('product'))

    def test_queries(self):
        """ Test that the total number of queries for a product/version that is in the report. """
        self.assertEqual(self.expected_queries, self._performance_report.queries(('.*[0-9][0-9].*', 'dummy')))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(0, self._performance_report.queries_violating_max_responsetime(('.*[0-9][0-9].*', 'dummy')))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(0, self._performance_report.queries_violating_wished_responsetime(('.*[0-9][0-9].*', 'dummy')))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2018, 1, 20, 2, 41, 52),
                         self._performance_report.datetime(('.*[0-9][0-9].*', 'dummy')))

    def test_date_without_urls(self):
        """ Test that the min date is returned if there are no report urls to consult. """
        class SilkPerformerWithoutUrls(SilkPerformerUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.datetime.min,
                         SilkPerformerWithoutUrls('http://report').datetime(('.*[0-9][0-9].*', 'dummy')))

    def test_duration(self):
        """ Test tha the duration of the test is correct. """
        self.assertEqual(datetime.timedelta(minutes=38, seconds=19),
                         self._performance_report.duration(('.*[0-9][0-9].*', 'dummy')))

    def test_duration_without_urls(self):
        """ Test that the max duration is returned if there are no report urls to consult. """
        class SilkPerformerWithoutUrls(SilkPerformerUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.timedelta.max,
                         SilkPerformerWithoutUrls('http://report').duration(('.*[0-9][0-9].*', 'dummy')))


class SilkPerformerMultipleReportsTest(SilkPerformerTest):
    """ Unit tests for the Silk Performer performance report metric source with multiple reports. """

    expected_queries = 2 * SilkPerformerTest.expected_queries

    def setUp(self):
        self._performance_report = SilkPerformerUnderTest('http://report/',
                                                          report_urls=['http://report/1', 'http://report/2'])


class SilkPerformerInvalidReportTest(unittest.TestCase):
    """ Unit tests for an invalid (missing Responsetimes header) Silk Performer performance report metric source. """

    def test_queries_max_responsetime_with_invalid_report(self):
        """ Test that the value of an invalid report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://invalid/').queries_violating_max_responsetime('p2'))

    def test_date_with_invalid_report(self):
        """ Test that the date of an invalid report is the min date. """
        self.assertEqual(datetime.datetime.min, SilkPerformerUnderTest('http://invalid/').datetime('p4'))

    def test_duration_with_invalid_report(self):
        """ Test that the duration of an invalid report is the max duration. """
        self.assertEqual(datetime.timedelta.max, SilkPerformerUnderTest('http://invalid/').duration('p5'))


class SilkPerformerMissingTest(unittest.TestCase):
    """ Unit tests for a missing Silk Performer performance report metric source. """

    def test_queries_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries('p1'))

    def test_queries_max_responsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries_violating_max_responsetime('p2'))

    def test_queries_wished_reponsetime_with_missing_report(self):
        """ Test that the value of a missing report is -1. """
        self.assertEqual(-1, SilkPerformerUnderTest('http://error/').queries_violating_wished_responsetime('p3'))

    def test_date_with_missing_report(self):
        """ Test that the date of a missing report is the min date. """
        self.assertEqual(datetime.datetime.min, SilkPerformerUnderTest('http://error/').datetime('p4'))

    def test_duration_with_missing_report(self):
        """ Test that the duration of a missing report is the max duration. """
        self.assertEqual(datetime.timedelta.max, SilkPerformerUnderTest('http://error/').duration('p5'))
