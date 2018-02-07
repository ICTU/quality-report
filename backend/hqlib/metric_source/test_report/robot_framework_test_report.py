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
from typing import List

import dateutil.parser

from ..abstract import test_report
from ..url_opener import UrlOpener
from ...typing import DateTime


class RobotFrameworkTestReport(test_report.TestReport):
    """ Class representing Robot Framework XML test reports. """

    metric_source_name = "Robot Framework test report"

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        return self.__test_count(metric_source_id, "pass")

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        return self.__test_count(metric_source_id, "fail")

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the report. """
        try:
            root = self.__element_tree(metric_source_id)
        except UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        except xml.etree.cElementTree.ParseError:
            return datetime.datetime.min
        try:
            return dateutil.parser.parse(root.get("generated"))
        except TypeError as reason:
            logging.error("Couldn't parse report date and time from %s: %s", metric_source_id, reason)
            return datetime.datetime.min

    def metric_source_urls(self, *report_urls: str) -> List[str]:  # pylint: disable=no-self-use
        return [re.sub(r"output\.xml$", "report.html", report_url) for report_url in report_urls]

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        try:
            root = self.__element_tree(report_url)
        except UrlOpener.url_open_exceptions:
            return -1
        except xml.etree.cElementTree.ParseError:
            return -1
        try:
            return int(root.findall("statistics/total/stat")[1].get(result_type, -1))
        except IndexError as reason:
            logging.error("Can't find %s test count in %s: %s", result_type, report_url, reason)
            return -1

    def __element_tree(self, report_url: str) -> Element:
        """ Return the report contents as ElementTree. """
        contents = self._url_read(report_url)
        try:
            return xml.etree.cElementTree.fromstring(contents)
        except xml.etree.cElementTree.ParseError as reason:
            logging.error("Couldn't parse report at %s: %s", report_url, reason)
            raise
