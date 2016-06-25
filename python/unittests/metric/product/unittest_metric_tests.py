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

import unittest

from qualitylib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument
    def __init__(self, line_coverage=0, branch_coverage=0, unittests=10):
        self.__line_coverage = line_coverage
        self.__branch_coverage = branch_coverage
        self.__unittests = unittests
        self.__failing_unittests = 5 if unittests else 0

    def unittest_line_coverage(self, *args):
        """ Return the percentage line coverage. """
        return self.__line_coverage

    def unittest_branch_coverage(self, *args):
        """ Return the percentage branch coverage. """
        return self.__branch_coverage

    def unittests(self, *args):
        """ Return the number of unittests. """
        return self.__unittests

    def failing_unittests(self, *args):
        """ Return the number of failing unittests. """
        return self.__failing_unittests

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'


class FakeSubject(object):
    """ Provide for a fake subject. """
    def __init__(self, sonar=None, unittests=True, integration_tests=False):
        self.__unittests = domain.Product(domain.Project(), metric_source_ids={sonar: 'some:fake:id'}) \
            if unittests else None
        self.__integration_tests = domain.Product(domain.Project(), metric_source_ids={sonar: 'some:fake:id'}) \
            if integration_tests else None

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def unittests(self):
        """ Return the unit tests of the subject. """
        return self.__unittests

    def integration_tests(self):
        """ Return the integration tests of the subject. """
        return self.__integration_tests


class SonarDashboardUrlTestMixin(object):
    # pylint: disable=too-few-public-methods
    """ Mixin for metrics whose url refers to the Sonar dashboard. """
    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), self._metric.url())


class FailingUnittestsTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    """ Unit tests for the failing unit tests metric. """

    def setUp(self):
        self.__sonar = FakeSonar(line_coverage=89)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self._metric = metric.FailingUnittests(subject=FakeSubject(self.__sonar), project=project)

    def test_value(self):
        """ Test that the value of the metric equals the line coverage reported by Sonar. """
        self.assertEqual(5, self._metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('5 van de 10 unittesten falen.', self._metric.report())

    def test_status_with_zero_unittests(self):
        sonar = FakeSonar(unittests=0)
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        failing_unittests = metric.FailingUnittests(subject=FakeSubject(sonar), project=project)
        self.assertEqual('red', failing_unittests.status())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Sonar and the product has unit tests. """
        product = FakeSubject(self.__sonar)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.assertTrue(metric.FailingUnittests.can_be_measured(product, project))

    def test_cant_be_measured_without_unittests(self):
        """ Test that the metric can only be measured when the product has unit tests. """
        product = FakeSubject()
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.assertFalse(metric.FailingUnittests.can_be_measured(product, project))

    def test_cant_be_measured_without_sonar(self):
        """ Test that the metric can only be measured when the project has Sonar. """
        product = FakeSubject(self.__sonar)
        project = domain.Project()
        self.assertFalse(metric.FailingUnittests.can_be_measured(product, project))


class UnittestLineCoverageTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    """ Unit tests for the unit test line coverage metric. """

    def setUp(self):
        self.__sonar = FakeSonar(line_coverage=89)
        self.__project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.__product = FakeSubject(self.__sonar)
        self._metric = metric.UnittestLineCoverage(subject=self.__product, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the line coverage reported by Sonar. """
        self.assertEqual(89, self._metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject unittest line coverage is 89% (10 unittests).', self._metric.report())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Sonar and the product has unit tests. """
        product = FakeSubject(self.__sonar)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.assertTrue(metric.UnittestLineCoverage.can_be_measured(product, project))

    def test_cant_be_measured_without_unittests(self):
        """ Test that the metric can only be measured when the product has unit tests. """
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        product = domain.Product(project)
        self.assertFalse(metric.UnittestLineCoverage.can_be_measured(product, project))

    def test_cant_be_measured_without_sonar(self):
        """ Test that the metric can only be measured when the project has Sonar. """
        product = FakeSubject(self.__sonar)
        project = domain.Project()
        self.assertFalse(metric.UnittestLineCoverage.can_be_measured(product, project))

    def test_wont_be_measured_with_integration_tests(self):
        """ Test that the metric isn't measured when the product also has integration tests since then the combined
            unit and integration test coverage will be measured instead. """
        product = FakeSubject(self.__sonar, integration_tests=True)
        self.assertFalse(metric.UnittestLineCoverage.can_be_measured(product, self.__project))


class UnittestBranchCoverageTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    """ Unit tests for the unit test branch coverage metric. """

    def setUp(self):
        self.__sonar = FakeSonar(branch_coverage=87)
        self.__project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self._metric = metric.UnittestBranchCoverage(subject=FakeSubject(self.__sonar), project=self.__project)

    def test_value(self):
        """ Test that the value of the metric equals the branch coverage reported by Sonar. """
        self.assertEqual(87, self._metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject unittest branch coverage is 87% (10 unittests).', self._metric.report())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Sonar and the product has unit tests. """
        product = FakeSubject(self.__sonar)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.assertTrue(metric.UnittestBranchCoverage.can_be_measured(product, project))

    def test_cant_be_measured_without_unittests(self):
        """ Test that the metric can only be measured when the product has unit tests. """
        product = FakeSubject()
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self.assertFalse(metric.UnittestBranchCoverage.can_be_measured(product, project))

    def test_cant_be_measured_without_sonar(self):
        """ Test that the metric can only be measured when the project has Sonar. """
        product = FakeSubject(self.__sonar)
        project = domain.Project()
        self.assertFalse(metric.UnittestBranchCoverage.can_be_measured(product, project))

    def test_wont_be_measured_with_integration_tests(self):
        """ Test that the metric isn't measured when the product also has integration tests since then the combined
            unit and integration test coverage will be measured instead. """
        product = FakeSubject(self.__sonar, integration_tests=True)
        self.assertFalse(metric.UnittestBranchCoverage.can_be_measured(product, self.__project))
