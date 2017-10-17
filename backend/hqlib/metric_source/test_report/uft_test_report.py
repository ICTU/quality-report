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
import logging
import xml.etree.cElementTree
from xml.etree.ElementTree import Element

from ..abstract import test_report
from ..url_opener import UrlOpener
from ...typing import DateTime


class UFTTestReport(test_report.TestReport):
    """ Class representing HP UFT XML test reports. """

    metric_source_name = 'UFT test report'

    def _passed_tests(self, report_url: str) -> int:
        """ Return the number of passed tests. """
        return self.__test_count(report_url, 'passed')

    def _failed_tests(self, report_url: str) -> int:
        """ Return the number of failed tests. """
        return self.__test_count(report_url, 'failed')

    def _report_datetime(self, report_url: str) -> DateTime:
        """ Return the date and time of the report. """
        try:
            summary = self.__summary(report_url)
        except UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        except xml.etree.cElementTree.ParseError:
            return datetime.datetime.min
        try:
            date_string, time_string = summary.get('eTime').split(' - ')
        except AttributeError as reason:
            logging.error("UFT report summary at %s has no e(nd)Time attribute: %s", report_url, reason)
            return datetime.datetime.min
        day, month, year = date_string.split('-')
        hour, minute, second = time_string.split(':')
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        try:
            summary = self.__summary(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        except xml.etree.cElementTree.ParseError:
            return -1
        return int(summary.get(result_type, -1))

    def __summary(self, report_url: str) -> Element:
        """ Return the summary in the report. """
        root = self.__element_tree(report_url)
        return root.find('./Doc/Summary')

    def __element_tree(self, report_url: str) -> Element:
        """ Return the report contents as ElementTree. """
        contents = self._url_read(report_url)
        try:
            return xml.etree.cElementTree.fromstring(contents)
        except xml.etree.cElementTree.ParseError as reason:
            logging.error("Couldn't parse report at %s: %s", report_url, reason)
            raise
