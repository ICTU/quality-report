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

    metric_source_name = metric_source.Sonar.metric_source_name

    def __init__(self, line_coverage=0, branch_coverage=0):
        self.__line_coverage = line_coverage
        self.__branch_coverage = branch_coverage

    # pylint: disable=unused-argument

    def overall_test_line_coverage(self, *args):
        """ Return the percentage line coverage. """
        return self.__line_coverage

    def overall_test_branch_coverage(self, *args):
        """ Return the percentage branch coverage. """
        return self.__branch_coverage

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'


class FakeSubject(object):
    """ Provide for a fake subject. """

    def __init__(self, sonar=None, unittests=True, integration_tests=True):
        self.__unittests = domain.Product(domain.Project(), metric_source_ids={sonar: 'some:fake:id'}) \
            if unittests else None
        self.__integration_tests = domain.Product(domain.Project(), metric_source_ids={sonar: 'some:fake:id'}) \
            if integration_tests else None

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    # pylint: disable=unused-argument

    @staticmethod
    def metric_source_id(*args):
        """ Return a product id. """
        return 'some:fake:id'

    def unittests(self):
        """ Return the unit tests of the subject. """
        return self.__unittests

    def integration_tests(self):
        """ Return the integration tests of the subject. """
        return self.__integration_tests


class CommonUnitAndIntegrationTestMetricTestsMixin(object):
    """ Mixin for metrics whose url refers to the Sonar dashboard. """

    class_under_test = domain.Metric  # Subclass responsibility
    expected_value = 0  # Subclass responsibility
    expected_report = 'Subclass responsibility'

    def setUp(self):  # pylint: disable=invalid-name
        """ Create the fixture for the unit tests. """
        self.__sonar = FakeSonar(line_coverage=self.expected_value, branch_coverage=self.expected_value)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.__product = FakeSubject(self.__sonar)
        self.__metric = self.class_under_test(subject=self.__product, project=project)

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
        """ Test that the metric is applicable when the product has both unit tests and integration tests. """
        self.assertTrue(self.class_under_test.is_applicable(self.__product))

    def test_is_not_applicable(self):
        """ Test that the metric is not applicable if the product has only unit tests. """
        product = FakeSubject(self.__sonar, integration_tests=False)
        self.assertFalse(self.class_under_test.is_applicable(product))


class UnitAndIntegrationTestLineCoverageTest(CommonUnitAndIntegrationTestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the combined unit en integration test line coverage metric. """

    class_under_test = metric.UnitAndIntegrationTestLineCoverage
    expected_value = 89
    expected_report = 'FakeSubject gecombineerde unit- en integratietest line coverage is 89%.'


class UnitAndIntegrationTestBranchCoverageTest(CommonUnitAndIntegrationTestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the combined unit and integration test branch coverage metric. """

    class_under_test = metric.UnitAndIntegrationTestBranchCoverage
    expected_value = 87
    expected_report = 'FakeSubject gecombineerde unit- en integratietest branch coverage is 87%.'
