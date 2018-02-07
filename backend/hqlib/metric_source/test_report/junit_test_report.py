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
import logging
import re
import xml.etree.cElementTree
from xml.etree.ElementTree import Element
from typing import List, Sequence

from ..abstract import test_report
from ..url_opener import UrlOpener
from ... import utils
from ...typing import DateTime


class JunitTestReport(test_report.TestReport):
    """ Class representing Junit test reports. """

    metric_source_name = 'Junit test report'

    def metric_source_urls(self, *report_urls: str) -> List[str]:
        return [re.sub(r'junit/junit\.xml$', 'html/htmlReport.html', report_url) for report_url in report_urls]

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        failed = self._failed_tests(metric_source_id)
        skipped = self._skipped_tests(metric_source_id)
        total = self.__test_count(metric_source_id, 'tests')
        return -1 if -1 in (failed, skipped, total) else total - (skipped + failed)

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        failed = self.__failure_count(metric_source_id)
        errors = self.__test_count(metric_source_id, 'errors')
        return -1 if -1 in (failed, errors) else failed + errors

    def _skipped_tests(self, metric_source_id: str) -> int:
        """ Return the number of skipped tests. """
        skipped = self.__test_count(metric_source_id, 'skipped')
        disabled = self.__test_count(metric_source_id, 'disabled')
        return -1 if -1 in (skipped, disabled) else skipped + disabled

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the report. """
        try:
            test_suites = self.__test_suites(metric_source_id)
        except UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        except xml.etree.cElementTree.ParseError:
            return datetime.datetime.min
        if test_suites:
            timestamps = [test_suite.get('timestamp') for test_suite in test_suites]
            date_times = [utils.parse_iso_datetime(timestamp + 'Z') for timestamp in timestamps if timestamp]
            if date_times:
                return min(date_times)
            logging.warning("Couldn't find timestamps in test suites in: %s", metric_source_id)
            return datetime.datetime.min
        logging.warning("Couldn't find test suites in: %s", metric_source_id)
        return datetime.datetime.min

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        try:
            test_suites = self.__test_suites(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        except xml.etree.cElementTree.ParseError:
            return -1
        if test_suites:
            return sum(int(test_suite.get(result_type, 0)) for test_suite in test_suites)
        logging.warning("Couldn't find test suites in: %s", report_url)
        return -1

    def __failure_count(self, report_url: str) -> int:
        """ Return the number of test cases that have failures (failed assertions). """
        try:
            root = self.__element_tree(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        except xml.etree.cElementTree.ParseError:
            return -1
        return len(root.findall('.//testcase[failure]'))

    def __test_suites(self, report_url: str) -> Sequence[Element]:
        """ Return the test suites in the report. """
        root = self.__element_tree(report_url)
        return [root] if root.tag == 'testsuite' else root.findall('testsuite')

    def __element_tree(self, report_url: str) -> Element:
        """ Return the report contents as ElementTree. """
        contents = self._url_read(report_url)
        try:
            return xml.etree.cElementTree.fromstring(contents)
        except xml.etree.cElementTree.ParseError as reason:
            logging.error("Couldn't parse report at %s: %s", report_url, reason)
            raise
