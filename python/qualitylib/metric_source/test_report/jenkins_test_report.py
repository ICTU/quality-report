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

from ..abstract import test_report
from ... import utils
from ..url_opener import UrlOpener


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
        url = report_url
        if not url.endswith('/'):
            url += '/'
        url += 'lastCompletedBuild/testReport/api/python'
        try:
            contents = self._url_open(url).read()
        except UrlOpener.url_open_exceptions:
            return -1
        try:
            report_dict = eval(contents)
        except (SyntaxError, NameError, TypeError) as reason:
            logging.warn("Couldn't eval %s to read test count %s: %s\nData received: %s",
                         url, result_type, reason, contents)
            return -1
        return int(report_dict[result_type])

    def _report_datetime(self, report_url):
        """ Return the date and time of the specified report. """
        url = report_url
        if not url.endswith('/'):
            url += '/'
        url += 'lastCompletedBuild/api/python'
        try:
            contents = self._url_open(url).read()
        except UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        try:
            report_dict = eval(contents)
        except (SyntaxError, NameError, TypeError) as reason:
            logging.warn("Couldn't eval %s to read date and time: %s\nData received: %s", url, reason, contents)
            return datetime.datetime.min
        return datetime.datetime.fromtimestamp(float(report_dict["timestamp"])/1000.)
