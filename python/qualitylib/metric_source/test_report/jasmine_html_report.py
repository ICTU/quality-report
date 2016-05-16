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

import re
import urllib2

from .. import beautifulsoup
from ..abstract import test_report


class JasmineHTMLReport(test_report.TestReport):
    """ Class representing Jasmine HTML test reports. """
    metric_source_name = 'Jasmine HTML testreport'
    needs_metric_source_id = True

    def _passed_tests(self, report_url):
        """ Return the number of passed tests as reported by the test report. """
        try:
            soup = beautifulsoup.BeautifulSoup(self._url_open(report_url))
        except urllib2.HTTPError:
            nr_passed = -1
        else:
            nr_passed = self.__parse_passed_tests(soup)
        return nr_passed

    def _failed_tests(self, report_url):
        """ Return the number of failed tests as reported by the test report. """
        try:
            soup = beautifulsoup.BeautifulSoup(self._url_open(report_url))
        except urllib2.HTTPError:
            nr_failed = -1
        else:
            nr_failed = self.__parse_failed_tests(soup)
        return nr_failed

    def _skipped_tests(self, report_url):
        """ Return the number of skipped tests as reported by the test report. """
        return 0  # Jasmine reports don't have skipped tests.

    @staticmethod
    def __parse_passed_tests(soup):
        """ Get the number of passed tests from the HTML soup. """
        last_div_string = str(soup('div')[-1])
        match = re.search(r'<b>Total tests passed</b>: (\d+) ', last_div_string)
        return int(match.group(1)) if match else -1

    @staticmethod
    def __parse_failed_tests(soup):
        """ Get the number of failed tests from the HTML soup. """
        last_div_string = str(soup('div')[-1])
        match = re.search(r'<b>Total tests failed</b>: (\d+) ', last_div_string)
        return int(match.group(1)) if match else -1
