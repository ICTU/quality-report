"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

from __future__ import absolute_import

import datetime
import logging
import xml.etree.ElementTree

from ..abstract import test_report
from ... import utils
from ..url_opener import UrlOpener


class JunitTestReport(test_report.TestReport):
    """ Class representing Junit test reports. """
    metric_source_name = 'Junit test report'
    needs_metric_source_id = True

    def _passed_tests(self, report_url):
        """ Return the number of passed tests. """
        failed = self._failed_tests(report_url)
        skipped = self._skipped_tests(report_url)
        total = self.__test_count(report_url, 'tests')
        if -1 in (failed, skipped, total):
            return -1
        else:
            return total - (skipped + failed)

    def _failed_tests(self, report_url):
        """ Return the number of failed tests. """
        failures = self.__test_count(report_url, 'failures')
        errors = self.__test_count(report_url, 'errors')
        if -1 in (failures, errors):
            return -1
        else:
            return failures + errors

    def _skipped_tests(self, report_url):
        """ Return the number of skipped tests. """
        skipped = self.__test_count(report_url, 'skipped')
        disabled = self.__test_count(report_url, 'disabled')
        if -1 in (skipped, disabled):
            return -1
        else:
            return skipped + disabled

    def _report_datetime(self, report_url):
        """ Return the date and time of the report. """
        try:
            test_suites = self.__test_suites(report_url)
        except UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        if test_suites:
            timestamps = [test_suite.get('timestamp', None) for test_suite in test_suites]
            date_times = [utils.parse_iso_datetime(timestamp + 'Z') for timestamp in timestamps if timestamp]
            if date_times:
                return min(date_times)
            else:
                logging.warn("Couldn't find timestamps in test suites in: %s", report_url)
                return datetime.datetime.min
        else:
            logging.warn("Couldn't find test suites in: %s", report_url)
            return datetime.datetime.min

    @utils.memoized
    def __test_count(self, report_url, result_type):
        """ Return the number of tests with the specified result in the test report. """
        try:
            test_suites = self.__test_suites(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        if test_suites:
            return sum(int(test_suite.get(result_type, 0)) for test_suite in test_suites)
        else:
            logging.warn("Couldn't find test suites in: %s", report_url)
            return -1

    def __test_suites(self, report_url):
        """ Return the test suites in the report. """
        contents = self._url_open(report_url).read()
        root = xml.etree.ElementTree.fromstring(contents)
        return [root] if root.tag == 'testsuite' else root.findall('testsuite')

