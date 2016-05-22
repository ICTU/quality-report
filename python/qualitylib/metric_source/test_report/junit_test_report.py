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

import logging
import urllib2
import xml.etree.ElementTree

from ..abstract import test_report
from ... import utils


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

    @utils.memoized
    def __test_count(self, report_url, result_type):
        """ Return the number of tests with the specified result in the test report. """
        try:
            contents = self._url_open(report_url).read()
        except (urllib2.HTTPError, urllib2.URLError) as reason:
            logging.warn("Couldn't open %s to read test count %s: %s", report_url, result_type, reason)
            return -1
        root = xml.etree.ElementTree.fromstring(contents)
        test_suites = [root] if root.tag == 'testsuite' else root.findall('testsuite')
        if test_suites:
            return sum(int(test_suite.get(result_type, 0)) for test_suite in test_suites)
        else:
            logging.warn("Couldn't find test suites in: %s", report_url)
            return -1
