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

import unittest

from hqlib import metric, domain, metric_source


class CommonUnittestMetricTestsMixin(object):
    """ Mixin for common unit tests. """

    class_under_test = domain.Metric  # Subclass responsibility
    expected_value = 0  # Subclass responsibility
    expected_report = 'Subclass responsibility'

    def setUp(self):  # pylint: disable=invalid-name
        """ Set up the fixture for the unit tests. """
        self.__report = unittest.mock.MagicMock()
        self.__report.statement_coverage.return_value = 89
        self.__report.branch_coverage.return_value = 87
        self.__report.dashboard_url.return_value = "http://sonar/id"
        self.__report.metric_source_name = "SonarQube coverage report"
        self.__report.metric_source_urls.return_value = ["http://sonar/id"]
        project = domain.Project(metric_sources={metric_source.UnittestCoverageReport: self.__report})
        self.__subject = unittest.mock.MagicMock()
        self.__subject.name.return_value = "FakeSubject"
        self.__metric = self.class_under_test(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the value reported by Sonar. """
        self.assertEqual(self.expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual(self.expected_report, self.__metric.report())


class UnittestLineCoverageTest(CommonUnittestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the unit test line coverage metric. """

    class_under_test = metric.UnittestLineCoverage
    expected_value = 89
    expected_report = 'FakeSubject unittest line coverage is 89%.'


class UnittestBranchCoverageTest(CommonUnittestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the unit test branch coverage metric. """

    class_under_test = metric.UnittestBranchCoverage
    expected_value = 87
    expected_report = 'FakeSubject unittest branch coverage is 87%.'
