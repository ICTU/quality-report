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
from __future__ import absolute_import

import ast
import datetime
import logging

from ..abstract import test_report
from ..url_opener import UrlOpener
from ... import utils


class JenkinsTestReport(test_report.TestReport):
    """ Class representing Jenkins test reports. """
    metric_source_name = 'Jenkins testreport'
    needs_metric_source_id = True

    def _passed_tests(self, report_url):
        """ Return the number of passed tests. """
        try:
            return self.__test_count(report_url, 'passCount')
        except KeyError:
            # Surefire reports don't have a pass count, calculate it:
            total = self.__test_count(report_url, 'totalCount')
            skipped = self._skipped_tests(report_url)
            failed = self._failed_tests(report_url)
            return total - skipped - failed

    def _failed_tests(self, report_url):
        """ Return the number of failed tests. """
        return self.__test_count(report_url, 'failCount')

    def _skipped_tests(self, report_url):
        """ Return the number of skipped tests. """
        return self.__test_count(report_url, 'skipCount')

    @utils.memoized
    def __test_count(self, report_url, result_type):
        """ Return the number of tests with the specified result in the test report. """
        json = self.__read_json(self.__join_url(report_url, 'lastCompletedBuild/testReport/api/python'))
        return int(json[result_type]) if json else -1

    def _report_datetime(self, report_url):
        """ Return the date and time of the specified report. """
        json = self.__read_json(self.__join_url(report_url, 'lastCompletedBuild/api/python'))
        return datetime.datetime.fromtimestamp(float(json["timestamp"])/1000.) if json else datetime.datetime.min

    def __read_json(self, api_url):
        """ Return the json from the url, or the default when something goes wrong. """
        try:
            contents = self._url_open(api_url).read()
        except UrlOpener.url_open_exceptions:
            return None
        try:
            return ast.literal_eval(contents)
        except (SyntaxError, NameError, TypeError) as reason:
            logging.warning("Couldn't eval %s: %s\nData received: %s", api_url, reason, contents)
            return None

    @staticmethod
    def __join_url(*parts):
        """ Join the different url parts with forward slashes. """
        return '/'.join([part.strip('/') for part in parts])
