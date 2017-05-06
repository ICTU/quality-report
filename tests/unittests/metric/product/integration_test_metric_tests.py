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

import unittest

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument

    metric_source_name = metric_source.Sonar.metric_source_name
    needs_metric_source_id = metric_source.Sonar.needs_metric_source_id

    def __init__(self, line_coverage=0, branch_coverage=0):
        self.__line_coverage = line_coverage
        self.__branch_coverage = branch_coverage

    def integration_test_line_coverage(self, *args):
        """ Return the percentage line coverage. """
        return self.__line_coverage

    def integration_test_branch_coverage(self, *args):
        """ Return the percentage branch coverage. """
        return self.__branch_coverage

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'


class FakeSubject(object):
    """ Provide for a fake subject. """
    def __init__(self, unittests=False, integration_tests=True):
        self.__has_unittests = unittests
        self.__has_integration_tests = integration_tests

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        return 'some:fake:id'

    def has_unittests(self):
        """ Return whether the subject has unit tests. """
        return self.__has_unittests

    def has_integration_tests(self):
        """ Return whether the subject has integration tests. """
        return self.__has_integration_tests


class CommonIntegrationtestMetricTestsMixin(object):
    """ Mixin for common unit tests for the integration test metrics. """

    class_under_test = domain.Metric  # Subclass responsibility
    expected_value = 0  # Subclass responsibility
    expected_report = 'Subclass responsibility'

    def setUp(self):
        """ Set up the test fixture for the unit tests. """
        self.__sonar = FakeSonar(line_coverage=self.expected_value, branch_coverage=self.expected_value)
        self.__project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.__metric = self.class_under_test(subject=FakeSubject(), project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the line coverage reported by Sonar. """
        self.assertEqual(self.expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual(self.expected_report, self.__metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({self.__sonar.metric_source_name: self.__sonar.dashboard_url()}, self.__metric.url())

    def test_is_applicable(self):
        """ Test that the metric is applicable. """
        self.assertTrue(self.class_under_test.is_applicable(FakeSubject()))

    def test_is_not_applicable_with_unittests(self):
        """ Test that the metric isn't applicable when the product also has unit tests since then the combined
            unit and integration test coverage will be measured instead. """
        product = FakeSubject(unittests=True)
        self.assertFalse(self.class_under_test.is_applicable(product))


class IntegrationtestLineCoverageTest(CommonIntegrationtestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the integration test line coverage metric. """

    class_under_test = metric.IntegrationtestLineCoverage
    expected_value = 89
    expected_report = 'FakeSubject integratietest line coverage is 89%.'


class IntegrationtestBranchCoverageTest(CommonIntegrationtestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the integration test branch coverage metric. """

    class_under_test = metric.IntegrationtestBranchCoverage
    expected_value = 87
    expected_report = 'FakeSubject integratietest branch coverage is 87%.'
