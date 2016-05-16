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
    def __init__(self, line_coverage=0, branch_coverage=0):
        self.__line_coverage = line_coverage
        self.__branch_coverage = branch_coverage

    def line_coverage(self, *args):
        """ Return the percentage line coverage. """
        return self.__line_coverage

    def branch_coverage(self, *args):
        """ Return the percentage branch coverage. """
        return self.__branch_coverage

    @staticmethod
    def unittests(*args):
        """ Return the number of unittests. """
        return 10

    @staticmethod
    def failing_unittests(*args):
        """ Return the number of failing unittests. """
        return 5

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'


class FakeSubject(object):  # pylint: disable=too-few-public-methods
    """ Provide for a fake subject. """
    def __init__(self, sonar=None):
        self.__sonar = sonar

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def unittests(self):
        """ Return the unit test Sonar id of the subject. """
        return domain.Product(domain.Project(),
                              metric_source_ids={self.__sonar: 'some:fake:id'}) if self.__sonar else None


class SonarDashboardUrlTestMixin(object):
    # pylint: disable=too-few-public-methods
    """ Mixin for metrics whose url refers to the Sonar dashboard. """
    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), self._metric.url())


class FailingUnittestsTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
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
        self.assertEqual('5 van de 10 unittests falen.', self._metric.report())

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
    # pylint: disable=too-many-public-methods
    """ Unit tests for the unit test line coverage metric. """

    def setUp(self):  # pylint: disable=invalid-name
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


class UnittestBranchCoverageTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the unit test branch coverage metric. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = FakeSonar(branch_coverage=87)
        project = domain.Project(metric_sources={metric_source.Sonar: self.__sonar})
        self._metric = metric.UnittestBranchCoverage(subject=FakeSubject(self.__sonar), project=project)

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
