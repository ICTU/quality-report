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
import unittest
import urllib.error
from typing import cast, IO

from hqlib.metric_source import ICTULRKPerformanceLoadTestReport


HTML = r"""
<html><body><table>
<tr>
<th bgcolor="white" align="left">sampler_label</th>
<th bgcolor="white" align="right">aggregate_report_count</th>
<th bgcolor="white" align="right">average</th>
<th bgcolor="white" align="right">aggregate_report_median</th>
<th bgcolor="white" align="right">aggregate_report_90%_line</th>
<th bgcolor="white" align="right">aggregate_report_min</th>
<th bgcolor="white" align="right">aggregate_report_max</th>
<th bgcolor="white" align="right">aggregate_report_error%</th>
<th bgcolor="white" align="right">aggregate_report_rate</th>
<th bgcolor="white" align="right">aggregate_report_bandwidth</th>
<th bgcolor="white" align="right">aggregate_report_stddev</th>
<th align="right">matched_pattern</th>
<th align="right">yellow_norm</th>
<th align="right">red_norm</th>
</tr>
<tr>
<td bgcolor="white" align="left">first script</td>
<td bgcolor="white" align="right">5</td>
<td bgcolor="white" align="right">388</td>
<td bgcolor="white" align="right">226</td>
<td bgcolor="green" align="right">232</td>
<td bgcolor="white" align="right">194</td>
<td bgcolor="white" align="right">1087</td>
<td bgcolor="white" align="right">0.00%</td>
<td bgcolor="white" align="right">.0</td>
<td bgcolor="white" align="right">1.0</td>
<td bgcolor="white" align="right">349.58</td>
<td align="right">^.*</td>
<td align="right">1000</td>
<td align="right">2000</td>
</tr>
<tr>
<td bgcolor="white" align="left">second script</td>
<td bgcolor="white" align="right">5</td>
<td bgcolor="white" align="right">7131</td>
<td bgcolor="white" align="right">7327</td>
<td bgcolor="red" align="right">7354</td>
<td bgcolor="white" align="right">6276</td>
<td bgcolor="white" align="right">7374</td>
<td bgcolor="white" align="right">0.00%</td>
<td bgcolor="white" align="right">.0</td>
<td bgcolor="white" align="right">8.0</td>
<td bgcolor="white" align="right">427.98</td>
<td align="right">^.*</td>
<td align="right">1000</td>
<td align="right">2000</td>
</tr>
<tr>
<td bgcolor="white" align="left">third script</td>
<td bgcolor="white" align="right">287</td>
<td bgcolor="white" align="right">105</td>
<td bgcolor="white" align="right">90</td>
<td bgcolor="green" align="right">110</td>
<td bgcolor="white" align="right">63</td>
<td bgcolor="white" align="right">1385</td>
<td bgcolor="white" align="right">0.00%</td>
<td bgcolor="white" align="right">.1</td>
<td bgcolor="white" align="right">6.0</td>
<td bgcolor="white" align="right">111.11</td>
<td align="right">^third.*</td>
<td align="right">1000</td>
<td align="right">3000</td>
</tr>
</table><p data-date="2017-05-24T17:03:30.102443">Report date: Wed May 24 17:03:30 2017</p></body></html>"""


class ReportUnderTest(ICTULRKPerformanceLoadTestReport):  # pylint: disable=too-few-public-methods
    """ Override the Silk Performer performance report to return the url as report contents. """

    def url_open(self, url: str, log_error: bool = True) -> IO:  # pylint: disable=no-self-use,unused-argument
        """ Return the static html. """
        if 'error' in url:
            raise urllib.error.URLError('reason')
        else:
            return cast(IO, io.StringIO(HTML))


class ICTULRKPerformanceReportTest(unittest.TestCase):
    """ Unit tests for the ICTU LRK performance report metric source. """
    expected_queries = 3
    expected_queries_violating_max_responsetime = 1

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
        """ Test that the total number of queries for a product/version that is in the report. """
        self.assertEqual(self.expected_queries, self._performance_report.queries(('.*script.*', 'dummy')))

    def test_queries_violating_max_responsetime(self):
        """ Test that the number of queries violating the maximum response times is zero. """
        self.assertEqual(self.expected_queries_violating_max_responsetime,
                         self._performance_report.queries_violating_max_responsetime(('.*script.*', 'dummy')))

    def test_queries_violating_wished_reponsetime(self):
        """ Test that the number of queries violating the wished response times is zero. """
        self.assertEqual(0, self._performance_report.queries_violating_wished_responsetime(('.*script.*', 'dummy')))

    def test_date_of_last_measurement(self):
        """ Test that the date of the last measurement is correctly parsed from the report. """
        self.assertEqual(datetime.datetime(2017, 5, 24, 17, 3, 30, 102443),
                         self._performance_report.datetime(('.*[0-9][0-9].*', 'dummy')))

    def test_date_without_urls(self):
        """ Test that the min date is passed if there are no report urls to consult. """
        class ICTULRKReportWithoutUrls(ReportUnderTest):
            """ Simulate missing urls. """
            def urls(self, product):  # pylint: disable=unused-argument
                return []

        self.assertEqual(datetime.datetime.min,
                         ICTULRKReportWithoutUrls('http://report').datetime(('.*[0-9][0-9].*', 'dummy')))


class ICTULRKPerformanceReportMultipleReportsTest(ICTULRKPerformanceReportTest):
    """ Unit tests for the ICTU LRK performance report metric source with multiple reports. """

    expected_queries = 2 * ICTULRKPerformanceReportTest.expected_queries
    expected_queries_violating_max_responsetime = \
        2 * ICTULRKPerformanceReportTest.expected_queries_violating_max_responsetime

    def setUp(self):
        self._performance_report = ReportUnderTest('http://report/',
                                                   report_urls=['http://report/1', 'http://report/2'])


class ICTULRKPerformanceReportMissingTest(unittest.TestCase):
    """ Unit tests for a missing ICTU LRK performance report metric source. """

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
