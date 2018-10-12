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


class HighRiskCheckmarxAlertsTest(unittest.TestCase):
    """ Unit tests for the high risk Checkmarx alerts metric. """

    class_under_test: Type[AlertsMetric] = metric.HighRiskCheckmarxAlertsMetric  # May be overridden

    def test_value(self):
        """ Test that value of the metric equals the number of warnings as reported by Jenkins. """
        checkmarx_report = MagicMock()
        checkmarx_report.nr_warnings = MagicMock(return_value=99)
        project = domain.Project(metric_sources={metric_source.Checkmarx: checkmarx_report})
        metric_object = self.class_under_test(subject=MagicMock(), project=project)

        self.assertEqual(99, metric_object.value())

    def test_value_multiple_jobs(self):
        """ Test that the value of the metric equals the number of warnings if there are multiple reports. """
        checkmarx_report = MagicMock()
        checkmarx_report.nr_warnings = MagicMock(return_value=99)
        project = domain.Project(metric_sources={metric_source.Checkmarx: checkmarx_report})
        subject = MagicMock()
        subject.metric_source_id.return_value = ['ms_1', 'ms_2']
        metric_object = self.class_under_test(subject=subject, project=project)

        self.assertEqual(99, metric_object.value())
        checkmarx_report.nr_warnings.assert_called_with(('ms_1', 'ms_2'), self.class_under_test.risk_level_key)

    def test_value_without_metric_source(self):
        """ Test that the value is -1 when no ZAP Scan report is provided. """
        alerts = self.class_under_test(subject=None, project=domain.Project())
        self.assertEqual(-1, alerts.value())

    def test_norm(self):
        """ Test that the norm is correct. """
        metric_object = self.class_under_test(subject=None, project=MagicMock())
        expected_norm = 'Het product heeft geen {} risico Checkmarx security waarschuwingen. ' \
                        'Meer dan {} is rood.'.format(self.class_under_test.risk_level,
                                                      self.class_under_test.low_target_value)
        self.assertEqual(expected_norm,
                         metric_object.norm_template.format(**metric_object.norm_template_default_values()))

    def test_extra_info_no_issues(self):
        """ Test that the extra info is returned correctly when there are no issues. """
        checkmarx_report = MagicMock()
        checkmarx_report.issues = MagicMock(
            return_value=[metric_source.Checkmarx.Issue('a_group', 'the_name', 'http://url', 3, 'New')])
        checkmarx_report.obtain_issues = MagicMock()
        project = domain.Project(metric_sources={metric_source.Checkmarx: checkmarx_report})
        subject = MagicMock()
        subject.metric_source_id.return_value = ['ms_1']
        metric_object = self.class_under_test(subject=subject, project=project)

        issues = metric_object.extra_info_rows()
        self.assertEqual(({'href': 'http://url', 'text': 'the name'}, 'a group', 3, 'New'), issues[0])
        checkmarx_report.obtain_issues.assert_called_once_with(['ms_1'], self.class_under_test.risk_level_key.title())


class MediumRiskCheckmarxAlertsTest(HighRiskCheckmarxAlertsTest):
    """ Unit tests for the medium risk level Checkmarx alert metric. """

    class_under_test = metric.MediumRiskCheckmarxAlertsMetric
