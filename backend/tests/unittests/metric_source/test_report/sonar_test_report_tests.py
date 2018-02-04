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
import unittest

from hqlib.metric_source import Sonar


class SonarTestReportTest(unittest.TestCase):
    """ Unit tests for the test report part of SonarQube. """
    def setUp(self):
        self.__test_report = Sonar('http://sonar/')

    def test_test_report(self):
        """ Test retrieving a Sonar test report. """
        self.__test_report.unittests = unittest.mock.Mock(return_value=11)
        self.__test_report.failing_unittests = unittest.mock.Mock(return_value=2)
        self.assertEqual(2, self.__test_report.failed_tests('sonar_id'))
        self.assertEqual(9, self.__test_report.passed_tests('sonar_id'))
        self.assertEqual(0, self.__test_report.skipped_tests('sonar_id'))

    def test_missing_url(self):
        """ Test that the default is returned when no Sonar ids are provided. """
        self.__test_report.unittests = unittest.mock.Mock(return_value=11)
        self.__test_report.failing_unittests = unittest.mock.Mock(return_value=2)
        self.assertEqual(-1, self.__test_report.failed_tests())
        self.assertEqual(-1, self.__test_report.passed_tests())
        self.assertEqual(-1, self.__test_report.skipped_tests())
        self.assertEqual(datetime.datetime.min, self.__test_report.datetime())

    def test_urls(self):
        """ Test that the urls point to the HTML versions of the reports. """
        self.__test_report.dashboard_url = unittest.mock.Mock(return_value='http://sonar/sonar_id')
        self.assertEqual(['http://sonar/sonar_id'], self.__test_report.metric_source_urls('sonar_id'))
