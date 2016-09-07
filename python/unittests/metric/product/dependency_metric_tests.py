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

    metric_source_name = metric_source.Sonar.metric_source_name

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    @staticmethod
    def package_cycles(*args):
        """ Return the number of package cycles. """
        return 1


class FakeSubject(object):
    """ Provide for a fake subject. """

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    @staticmethod
    def short_name():
        """ Return the short name of the subject. """
        return 'FS'

    @staticmethod
    def dependencies(**kwargs):  # pylint: disable=unused-argument
        """ Return the dependencies of the subject. """
        return [('product1', 'product1_version'), ('product2', '')]

    @staticmethod
    def metric_source_id(metric_source):  # pylint: disable=unused-argument
        """ Return the metric source id """
        return 'id'


class FakeReport(object):
    """ Fake a quality report. """

    @staticmethod
    def get_product(product, version):  # pylint: disable=unused-argument
        """ Return the specified product. """
        return FakeSubject()


class SnapshotDependenciesTest(unittest.TestCase):
    """ Unit tests for the snapshot dependencies metric. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.Pom: 'FakePom',
                                                 metric_source.VersionControlSystem: 'FakeVCS'})
        self.__metric = metric.SnapshotDependencies(subject=FakeSubject(), report=FakeReport(), project=project)

    def test_value(self):
        """ Test that the value of the metric equals the number of snapshot dependencies of the product. """
        self.assertEqual(1, self.__metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'product2:trunk': 'index.html#section_FS'}, self.__metric.url())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('FakeSubject heeft 1 afhankelijkheden op snapshot versies van andere producten.',
                         self.__metric.report())


class CyclicDependenciesTest(unittest.TestCase):
    """ Unit tests for the cyclic dependencies metric. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self.__subject = domain.Product(project, 'PR', name='FakeSubject')
        self._metric = metric.CyclicDependencies(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the number of cyclic dependencies between packages. """
        self.assertEqual(FakeSonar().package_cycles(), self._metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar.dashboard_url()}, self._metric.url())
