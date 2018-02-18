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


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument

    metric_source_name = metric_source.Sonar.metric_source_name
    ncloc_to_return = 123

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    url = dashboard_url

    def ncloc(self, *args):
        """ Return the number of non-comment LOC. """
        return self.ncloc_to_return


class FakeHistory(object):  # pylint: disable=too-few-public-methods
    """ Fake the history for testing purposes. """
    @staticmethod
    def recent_history(*args):  # pylint: disable=unused-argument
        """ Return a fake recent history. """
        return [100, 200]


class ProductLOCTest(unittest.TestCase):
    """ Unit tests for the product LOC metric. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: 'sonar id'})
        self._metric = metric.ProductLOC(subject=subject, project=project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 50000 regels code. Meer dan 100000 regels code is rood.", self._metric.norm())

    def test_value(self):
        """ Test that the value of the metric equals the NCLOC returned by Sonar. """
        self.assertEqual(FakeSonar().ncloc(), self._metric.value())

    def test_report(self):
        """ Test that the metric report is correct. """
        self.assertEqual("FakeSubject heeft 123 regels code.", self._metric.report())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar().dashboard_url()}, self._metric.url())


class TotalLOCTest(unittest.TestCase):
    """ Unit tests for the total LOC metric. """

    def setUp(self):
        self.__sonar = FakeSonar()
        project = domain.Project(
            metric_sources={metric_source.Sonar: self.__sonar, metric_source.History: FakeHistory()},
            metric_options={metric.TotalLOC: dict(target=1000000, low_target=2000000)},
            metric_source_ids={self.__sonar: 'dummy'})
        product1 = domain.Product(short_name='PR1', name='FakeSubject1', metric_source_ids={self.__sonar: 'sonar id1'})
        product2 = domain.Product(short_name='PR2', name='FakeSubject2', metric_source_ids={self.__sonar: 'sonar id2'})
        product_without_sonar_id = domain.Product(short_name='PW', name='ProductWithoutSonarId')
        test_product = domain.Product(short_name='TP', is_main=False, metric_source_ids={self.__sonar: 'sonar id'})
        project.add_product(product1)
        project.add_product(product2)
        # Add products that should be ignored:
        project.add_product(product_without_sonar_id)
        project.add_product(test_product)
        self.__metric = metric.TotalLOC(subject=project, project=project)

    def test_norm(self):
        """ Test that the norm is correct. """
        self.assertEqual("Maximaal 1000000 regels code. Meer dan 2000000 regels code is rood.",
                         self.__metric.norm())

    def test_value(self):
        """ Test that the value of the metric equals the sum of the NCLOC returned by Sonar. """
        self.assertEqual(2 * FakeSonar().ncloc(), self.__metric.value())

    def test_url(self):
        """ Test that the url refers to Sonar. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar().url()}, self.__metric.url())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('Het totaal aantal regels code voor de producten FakeSubject1, FakeSubject2, '
                         'ProductWithoutSonarId is 246 regels code.', self.__metric.report())

    def test_recent_history(self):
        """ Test that the recent history subtracts the minimum value of each value so that more data can be plotted. """
        self.assertEqual([0, 100], self.__metric.recent_history())

    def test_override_target(self):
        """ Test that the target can be overridden via the project. """
        self.assertEqual(1000000, self.__metric.target())

    def test_override_low_target(self):
        """ Test that the low target can be overridden via the project. """
        self.assertEqual(2000000, self.__metric.low_target())

    def test_technical_debt(self):
        """ Test that technical debt can be specified via the project. """
        project = domain.Project(
            metric_sources={metric_source.Sonar: self.__sonar, metric_source.History: FakeHistory()},
            metric_source_ids={self.__sonar: "dummy"},
            metric_options={metric.TotalLOC: dict(target=100, low_target=110,
                                                  debt_target=domain.TechnicalDebtTarget(150))})
        product = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={self.__sonar: 'sonar id'})
        project.add_product(product)
        total_loc = metric.TotalLOC(subject=project, project=project)
        self.assertEqual('grey', total_loc.status())

    def test_unavailable_sonar(self):
        """ Test that the value is -1 when Sonar is not available. """
        self.__sonar.ncloc_to_return = -1
        self.assertEqual(-1, self.__metric.value())
