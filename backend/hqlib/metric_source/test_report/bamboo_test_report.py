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
import xml.etree.cElementTree
from xml.etree.ElementTree import Element

import dateutil.parser

from ..abstract import test_report
from ..url_opener import UrlOpener
from ...typing import DateTime


class BambooTestReport(test_report.TestReport):
    """ Class representing Bamboo test reports. """

    metric_source_name = 'Bamboo test report'

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        return self.__test_count(metric_source_id, 'successfulTestCount')

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        return self.__test_count(metric_source_id, 'failedTestCount')

    def _skipped_tests(self, metric_source_id: str) -> int:
        """ Return the number of skipped tests. """
        return self.__test_count(metric_source_id, 'skippedTestCount')

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the report. """
        try:
            root = self.__element_tree(metric_source_id)
        except UrlOpener.url_open_exceptions + (xml.etree.cElementTree.ParseError,):
            return datetime.datetime.min
        try:
            date_time_string = root.find('buildCompletedDate').text
            # Parse the date time string timezone-aware, and then convert it a date time without time zones since we
            # use naive date times internally:
            return dateutil.parser.parse(date_time_string, ignoretz=False).astimezone().replace(tzinfo=None)
        except (AttributeError, ValueError, TypeError) as reason:
            logging.error("Couldn't parse date and time from %s at %s: %s", self.metric_source_name, metric_source_id,
                          reason)
            return datetime.datetime.min

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        try:
            root = self.__element_tree(report_url)
        except UrlOpener.url_open_exceptions + (xml.etree.cElementTree.ParseError,):
            return -1
        try:
            return int(root.find(result_type).text)
        except (AttributeError, ValueError, TypeError) as reason:
            logging.error("Couldn't parse %s from %s at %s: %s", result_type, self.metric_source_name, report_url,
                          reason)
            return -1

    def __element_tree(self, report_url: str) -> Element:
        """ Return the report contents as ElementTree. """
        contents = self._url_read(report_url)
        try:
            return xml.etree.cElementTree.fromstring(contents)
        except xml.etree.cElementTree.ParseError as reason:
            logging.error("Couldn't parse %s at %s: %s", self.metric_source_name, report_url, reason)
            raise
