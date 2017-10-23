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
import unittest

from hqlib.metric_source import SonarTestReport


class FakeSonar(object):
    """ Fake a SonarQube metric source. """
    # pylint: disable=unused-argument

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def unittests(sonar_id):
        """ Return the total number of unittests. """
        return 11

    @staticmethod
    def failing_unittests(sonar_id):
        """ Return the number of failing unittests. """
        return 2

    @staticmethod
    def datetime(sonar_id):
        """ Return the date and time of the last Sonar analysis. """
        return datetime.datetime(2016, 7, 7, 12, 26, 44)

    @staticmethod
    def dashboard_url(sonar_id):
        """ Return the url to the dashboard of the Sonar analysis. """
        return 'http://sonar/' + sonar_id


class SonarTestReportTest(unittest.TestCase):
    """ Unit tests for the Sonar test report class. """
    def setUp(self):
        self.__test_report = SonarTestReport('http://sonar/', sonar_class=FakeSonar)

    def test_test_report(self):
        """ Test retrieving a Sonar test report. """
        self.assertEqual(2, self.__test_report.failed_tests('sonar_id'))
        self.assertEqual(9, self.__test_report.passed_tests('sonar_id'))
        self.assertEqual(0, self.__test_report.skipped_tests('sonar_id'))

    def test_missing_url(self):
        """ Test that the default is returned when no Sonar ids are provided. """
        self.assertEqual(-1, self.__test_report.failed_tests())
        self.assertEqual(-1, self.__test_report.passed_tests())
        self.assertEqual(-1, self.__test_report.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__test_report.datetime())

    def test_report_datetime(self):
        """ Test that the date and time of the Sonar analysis is returned. """
        self.assertEqual(datetime.datetime(2016, 7, 7, 12, 26, 44), self.__test_report.datetime('url'))

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        self.assertEqual(['http://sonar/sonar_id'], self.__test_report.metric_source_urls('sonar_id'))
