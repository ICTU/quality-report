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


import ast
import datetime
import logging
from typing import Dict, Optional

from ..abstract import test_report
from ..url_opener import UrlOpener
from ...typing import DateTime


class JenkinsTestReport(test_report.TestReport):
    """ Class representing Jenkins test reports. """
    metric_source_name = 'Jenkins testreport'

    def _passed_tests(self, metric_source_id: str) -> int:
        """ Return the number of passed tests. """
        try:
            return self.__test_count(metric_source_id, 'passCount')
        except KeyError:
            # Surefire reports don't have a pass count, calculate it:
            total = self.__test_count(metric_source_id, 'totalCount')
            skipped = self._skipped_tests(metric_source_id)
            failed = self._failed_tests(metric_source_id)
            return total - skipped - failed

    def _failed_tests(self, metric_source_id: str) -> int:
        """ Return the number of failed tests. """
        return self.__test_count(metric_source_id, 'failCount')

    def _skipped_tests(self, metric_source_id: str) -> int:
        """ Return the number of skipped tests. """
        return self.__test_count(metric_source_id, 'skipCount')

    def __test_count(self, report_url: str, result_type: str) -> int:
        """ Return the number of tests with the specified result in the test report. """
        json = self.__read_json(self.__join_url(report_url, 'lastCompletedBuild/testReport/api/python'))
        return int(json[result_type]) if json else -1

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of the specified report. """
        json = self.__read_json(self.__join_url(metric_source_id, 'lastCompletedBuild/api/python'))
        return datetime.datetime.fromtimestamp(float(json["timestamp"]) / 1000.) if json else datetime.datetime.min

    def __read_json(self, api_url: str) -> Optional[Dict[str, int]]:
        """ Return the json from the url, or the default when something goes wrong. """
        try:
            contents = self._url_read(api_url)
        except UrlOpener.url_open_exceptions:
            return None
        try:
            return ast.literal_eval(contents)
        except (SyntaxError, NameError, TypeError) as reason:
            logging.warning("Couldn't eval %s: %s\nData received: %s", api_url, reason, contents)
            return None

    @staticmethod
    def __join_url(*parts: str) -> str:
        """ Join the different url parts with forward slashes. """
        return '/'.join([part.strip('/') for part in parts])
