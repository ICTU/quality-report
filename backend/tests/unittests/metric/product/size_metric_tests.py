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
from unittest.mock import MagicMock, patch

from hqlib import metric, domain, metric_source


class ProductLOCTest(unittest.TestCase):
    """ Unit tests for the product LOC metric. """

    def setUp(self):
        with patch.object(metric_source.Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
            sonar = metric_source.Sonar('unimportant')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        subject = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: 'sonar id'})
        self._metric = metric.ProductLOC(subject=subject, project=project)

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_norm(self, mock_ncloc):
        """ Test that the norm is correct. """
        mock_ncloc.return_value = 123
        self.assertEqual("Maximaal 50000 regels code. Meer dan 100000 regels code is rood.", self._metric.norm())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_value(self, mock_ncloc):
        """ Test that the value of the metric equals the NCLOC returned by Sonar. """
        mock_ncloc.return_value = 123
        self.assertEqual(123, self._metric.value())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_report(self, mock_ncloc):
        """ Test that the metric report is correct. """
        mock_ncloc.return_value = 123
        self.assertEqual("FakeSubject heeft 123 regels code.", self._metric.report())

    @patch.object(metric_source.Sonar6, 'dashboard_url')
    def test_url(self, mock_dashboard_url):
        """ Test that the url is correct. """
        mock_dashboard_url.return_value = 'http://sonar'
        self.assertEqual({'SonarQube': 'http://sonar'}, self._metric.url())


class TotalLOCTest(unittest.TestCase):
    """ Unit tests for the total LOC metric. """

    def setUp(self):
        with patch.object(metric_source.Sonar, 'version_number') as mock_version_number:
            mock_version_number.return_value = '6.3'
            self.__sonar = metric_source.Sonar('unimportant')
        project = domain.Project(
            metric_sources={metric_source.Sonar: self.__sonar, metric_source.History: metric_source.CompactHistory('')},
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

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_norm(self, mock_ncloc):
        """ Test that the norm is correct. """
        mock_ncloc.return_value = 123
        self.assertEqual("Maximaal 1000000 regels code. Meer dan 2000000 regels code is rood.",
                         self.__metric.norm())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_value(self, mock_ncloc):
        """ Test that the value of the metric equals the sum of the NCLOC returned by Sonar. """
        mock_ncloc.return_value = 123
        self.assertEqual(2 * 123, self.__metric.value())

    @patch.object(metric_source.Sonar6, 'url')
    def test_url(self, mock_url):
        """ Test that the url refers to Sonar. """
        mock_url.return_value = 'http://sonar'
        self.assertEqual({'SonarQube': 'http://sonar'}, self.__metric.url())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_report(self, mock_ncloc):
        """ Test that the report is correct. """
        mock_ncloc.return_value = 123
        self.assertEqual('Het totaal aantal regels code voor de producten FakeSubject1, FakeSubject2, '
                         'ProductWithoutSonarId is 246 regels code.', self.__metric.report())

    @patch.object(metric_source.CompactHistory, 'recent_history')
    def test_recent_history(self, mock_recent_history):
        """ Test that the recent history subtracts the minimum value of each value so that more data can be plotted. """
        mock_recent_history.return_value = [0, None, 100]
        self.assertEqual([0, 100], self.__metric.recent_history())

    def test_override_target(self):
        """ Test that the target can be overridden via the project. """
        self.assertEqual(1000000, self.__metric.target())

    def test_override_low_target(self):
        """ Test that the low target can be overridden via the project. """
        self.assertEqual(2000000, self.__metric.low_target())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_technical_debt(self, mock_ncloc):
        """ Test that technical debt can be specified via the project. """

        project = domain.Project(
            metric_sources={metric_source.Sonar: self.__sonar, metric_source.History: MagicMock()},
            metric_source_ids={self.__sonar: "dummy"},
            metric_options={metric.TotalLOC: dict(target=100, low_target=110,
                                                  debt_target=domain.TechnicalDebtTarget(150))})
        product = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={self.__sonar: 'sonar id'})
        project.add_product(product)
        total_loc = metric.TotalLOC(subject=project, project=project)

        mock_ncloc.return_value = 111
        self.assertEqual('grey', total_loc.status())

    @patch.object(metric_source.Sonar6, 'ncloc')
    def test_unavailable_sonar(self, mock_ncloc):
        """ Test that the value is -1 when Sonar is not available. """
        mock_ncloc.return_value = -1
        self.assertEqual(-1, self.__metric.value())
