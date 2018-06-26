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
from unittest.mock import patch


from hqlib.metric_source import Sonar, Sonar6


class SonarCoverageReportTest(unittest.TestCase):
    """ Unit tests for the coverage report part of SonarQube. """

    # pylint: disable=no-member

    def setUp(self):
        with patch.object(Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
            self.coverage_report = Sonar('http://sonar/')

    @patch.object(Sonar6, "unittest_line_coverage")
    def test_statement_coverage(self, unittest_line_coverage):
        """ Test that the coverage report returns the statement coverage provided by SonarQube. """
        unittest_line_coverage.return_value = 80.
        self.assertEqual(80, self.coverage_report.statement_coverage("sonar_id"))

    @patch.object(Sonar6, "unittest_branch_coverage")
    def test_branch_coverage(self, unittest_branch_coverage):
        """ Test that the coverage report returns the branch coverage provided by SonarQube. """
        unittest_branch_coverage.return_value = 70.
        self.assertEqual(70, self.coverage_report.branch_coverage("sonar_id"))

    @patch.object(Sonar6, "datetime")
    def test_datetime(self, analysis_datetime):
        """ Test that the coverage report returns the statement coverage provided by SonarQube. """
        analysis_datetime.return_value = datetime.datetime(2017, 1, 1)
        self.assertEqual(datetime.datetime(2017, 1, 1), self.coverage_report.datetime("sonar_id"))

    @patch.object(Sonar6, "dashboard_url")
    def test_urls(self, dashboard_url):
        """ Test that the coverage report returns the urls provided by SonarQube. """
        dashboard_url.return_value = "http://sonar/sonar_id"
        self.assertEqual(["http://sonar/sonar_id"], self.coverage_report.metric_source_urls("sonar_id"))
