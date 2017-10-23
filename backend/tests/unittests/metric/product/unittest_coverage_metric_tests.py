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


class FakeUnitTestReport(metric_source.UnitTestReport):
    """ Provide for a fake unittest report object so that the unit test don't need access to an actual report
        instance. """
    # pylint: disable=unused-argument

    def __init__(self, line_coverage=0, branch_coverage=0, unittests=10):
        self.__line_coverage = line_coverage
        self.__branch_coverage = branch_coverage
        self.__unittests = unittests

    def unittest_line_coverage(self, *args):
        """ Return the percentage line coverage. """
        return self.__line_coverage

    def unittest_branch_coverage(self, *args):
        """ Return the percentage branch coverage. """
        return self.__branch_coverage

    def unittests(self, *args):
        """ Return the number of unittests. """
        return self.__unittests

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'


class FakeSubject(object):
    """ Provide for a fake subject. """
    def __init__(self, integration_tests=False):
        self.__has_integration_tests = integration_tests

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    @staticmethod
    def metric_source_id(*args):  # pylint: disable=unused-argument
        """ Return the metric source id for the test report. """
        return 'some:fake:id'

    def has_integration_tests(self):
        """ Return whether the subject has integration tests. """
        return self.__has_integration_tests


class CommonUnittestMetricTestsMixin(object):
    """ Mixin for common unit tests. """

    class_under_test = domain.Metric  # Subclass responsibility
    expected_value = 0  # Subclass responsibility
    expected_report = 'Subclass responsibility'

    def setUp(self):  # pylint: disable=invalid-name
        """ Set up the fixture for the unit tests. """
        self.__report = FakeUnitTestReport(line_coverage=self.expected_value, branch_coverage=self.expected_value)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__report})
        self.__metric = self.class_under_test(subject=FakeSubject(), project=project)

    def test_value(self):
        """ Test that the value of the metric equals the value reported by Sonar. """
        self.assertEqual(self.expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual(self.expected_report, self.__metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({self.__report.metric_source_name: self.__report.dashboard_url()}, self.__metric.url())

    def test_is_applicable(self):
        """ Test that the metric is applicable. """
        product = FakeSubject()
        self.assertTrue(self.class_under_test.is_applicable(product))


class UnittestLineCoverageTest(CommonUnittestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the unit test line coverage metric. """

    class_under_test = metric.UnittestLineCoverage
    expected_value = 89
    expected_report = 'FakeSubject unittest line coverage is 89% (10 unittests).'


class UnittestBranchCoverageTest(CommonUnittestMetricTestsMixin, unittest.TestCase):
    """ Unit tests for the unit test branch coverage metric. """

    class_under_test = metric.UnittestBranchCoverage
    expected_value = 87
    expected_report = 'FakeSubject unittest branch coverage is 87% (10 unittests).'
