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
from unittest.mock import MagicMock

from typing import Type

from hqlib import metric, domain, metric_source
from hqlib.metric.product.alerts_metrics import AlertsMetric


class HighRiskZAPScanAlertsTest(unittest.TestCase):
    """ Unit tests for the high risk ZAP Scan alerts metric. """

    class_under_test: Type[AlertsMetric] = metric.HighRiskZAPScanAlertsMetric  # noqa E701
    #   May be overridden

    def setUp(self):
        self.__zap_scan_report = MagicMock()
        self.__zap_scan_report.alerts = MagicMock(return_value=99)
        self.__zap_scan_report.metric_source_name = metric_source.ZAPScanReport.metric_source_name
        self.__subject = MagicMock()
        self.__subject.name = MagicMock(return_value='FakeSubject')
        self.__subject.metric_source_id = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.ZAPScanReport: self.__zap_scan_report})
        self.__metric = self.class_under_test(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the number of warnings as reported by Jenkins. """
        self.assertEqual(99, self.__metric.value())

    def test_extra_info_rows(self):
        """ Test that it returns the result of get_warnings_info of metric source object. """
        extra_info = [('xx', 'yy')]
        self.__zap_scan_report.get_warnings_info = MagicMock(return_value=extra_info)
        self.assertEqual(extra_info, self.__metric.extra_info_rows())

    def test_value_without_metric_source(self):
        """ Test that the value is -1 when no ZAP Scan report is provided. """
        self.__project = domain.Project(metric_sources={})
        self.__metric = self.class_under_test(subject=self.__subject, project=self.__project)
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        expected_report = 'FakeSubject heeft {0} {1} risico security waarschuwingen.'.format(
            99, self.class_under_test.risk_level)
        self.assertEqual(expected_report, self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        expected_norm = 'Het product heeft geen {} risico ZAP Scan security waarschuwingen. ' \
                        'Meer dan {} is rood.'.format(self.class_under_test.risk_level,
                                                      self.class_under_test.low_target_value)
        self.assertEqual(expected_norm,
                         self.__metric.norm_template.format(**self.__metric.norm_template_default_values()))

    def test_is_missing_without_zap_scan_report(self):
        """ Test that metric is missing when the ZAP Scan report is not available. """
        self.__metric = self.class_under_test(subject=self.__subject, project=domain.Project())
        self.assertTrue(self.__metric._missing())  # pylint: disable=protected-access

    def test_is_not_missing(self):
        """ Test that the metric is not missing when the report is available. """
        self.assertFalse(self.__metric._missing())  # pylint: disable=protected-access


class MediumRiskZAPScanAlertsTest(HighRiskZAPScanAlertsTest):
    """ Unit tests for the medium risk level ZAP Scan alert metric. """

    class_under_test = metric.MediumRiskZAPScanAlertsMetric
