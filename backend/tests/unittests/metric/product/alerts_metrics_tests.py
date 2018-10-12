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
from hqlib import domain, metric_source
from hqlib.metric.product.alerts_metrics import LowerIsBetterMetric, AlertsMetric


class AlertsMetricTest(unittest.TestCase):
    """ Unit tests for the AlertsMetric class metric. """

    def setUp(self):
        self.__project = domain.Project(metric_sources={metric_source.Checkmarx: None})
        self.__project.metric_sources = MagicMock(return_value=[None])
        self.__metric = AlertsMetric(subject=MagicMock(), project=self.__project)

    def test_alerts_metric_properties(self):
        """ Test the properties. """
        self.assertEqual('{name} heeft {value} {risk_level} risico {unit}.', self.__metric.template)
        self.assertEqual('Subclass responsibility', self.__metric.risk_level)
        self.assertEqual(0, self.__metric.target_value)

    @patch.object(LowerIsBetterMetric, 'norm_template_default_values')
    def test_norm_template_default_values(self, mock_super):
        """ Test the default values of norm template. """
        mock_super.return_value = {}

        result = self.__metric.norm_template_default_values()

        mock_super.assert_called_once()
        self.assertEqual({'risk_level': 'Subclass responsibility'}, result)

    def test_value(self):
        """ Test the value of number of alerts. """
        metric_source_object = MagicMock()
        metric_source_object.alerts = MagicMock(return_value=42)
        project = domain.Project(metric_sources={metric_source_object.Checkmarx: metric_source_object})
        project.metric_sources = MagicMock(return_value=[metric_source_object])
        metric_object = AlertsMetric(subject=MagicMock(), project=project)

        self.assertEqual(42, metric_object.value())
        self.assertEqual(metric_source_object.alerts.call_count, 2)

    def test_value_no_metric_source(self):
        """ Test the value of number of alerts, when there is no metric source. """
        self.assertEqual(-1, self.__metric.value())

    @patch.object(LowerIsBetterMetric, '_parameters')
    def test_parameters(self, mock_parameters):
        """ Test parameters of the norm. """
        mock_parameters.return_value = {'target': 3, 'low_target': 5, 'unit': 'bieps'}

        self.assertEqual('Maximaal 3 bieps. Meer dan 5 bieps is rood.', self.__metric.norm())
        mock_parameters.assert_called_once()
