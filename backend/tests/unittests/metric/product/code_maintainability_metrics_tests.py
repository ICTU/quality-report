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

from hqlib import domain, metric_source
from hqlib.metric import MaintainabilityBugs, Vulnerabilities, CodeSmells


class CodeMaintainabilityMetricTest(unittest.TestCase):
    """ Unit tests for the CodeMaintainabilityMetric metric class. """
    def test_extra_info_rows(self):
        """ Test if function correctly calls metric source function and formats the result. """
        sonar = MagicMock()
        sonar.violations_type_severity = MagicMock(
            side_effect=[('url_blocker', 1, '5min'), ('url_critical', 3, '10min'), ('url_major', 5, '15min'),
                         ('url_minor', 7, '25min'), ('url_info', 11, '35min')]
        )
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='sonar_id')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        metric = MaintainabilityBugs(subject=subject, project=project)

        result = metric.extra_info_rows()

        self.assertEqual([
            ({'href': 'url_blocker', 'text': 'Blocker'}, 1, '5min'),
            ({'href': 'url_critical', 'text': 'Critical'}, 3, '10min'),
            ({'href': 'url_major', 'text': 'Major'}, 5, '15min'),
            ({'href': 'url_minor', 'text': 'Minor'}, 7, '25min'),
            ({'href': 'url_info', 'text': 'Info'}, 11, '35min'),
        ], result)
        self.assertEqual('Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.', metric.norm_template)
        self.assertEqual('{name} heeft {value} {unit}.', metric.template)
        self.assertEqual(5, sonar.violations_type_severity.call_count)
        self.assertEqual(
            {"severity": "Severity", "number": "Aantal__detail-column-number",
             "debt": "Geschatte oplostijd__detail-column-number"},
            metric.extra_info_headers)

    def test_value_no_metric_source(self):
        """ Test that the value is equal to -1 when there is no metric source. """
        sonar = MagicMock()
        sonar.maintainability_bugs = MagicMock(return_value=99)
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='sonar_id')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        project.metric_sources = MagicMock(return_value=[None])
        metric = MaintainabilityBugs(subject=subject, project=project)

        result = metric.value()

        self.assertEqual(-1, result)
        self.assertEqual(None, metric.extra_info_headers)
        sonar.maintainability_bugs.assert_not_called()


class MaintainabilityBugsTest(unittest.TestCase):
    """ Unit tests for the MaintainabilityBugs metric class. """
    def test_value(self):
        """ Test that the value is equal to the number reported by Sonar. """
        sonar = MagicMock()
        sonar.maintainability_bugs = MagicMock(return_value=99)
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='sonar_id')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        metric = MaintainabilityBugs(subject=subject, project=project)

        result = metric.value()

        self.assertEqual(99, result)
        self.assertEqual('Hoeveelheid maintainability bugs', metric.name)
        self.assertEqual('maintainability bugs', metric.unit)
        self.assertEqual(0, metric.target_value)
        self.assertEqual(3, metric.low_target_value)
        self.assertEqual('BUG', metric.violation_type)
        self.assertEqual('Maintainability bugs per severity', metric.url_label_text)
        sonar.maintainability_bugs.assert_called_once_with('sonar_id')


class VulnerabilitiesTest(unittest.TestCase):
    """ Unit tests for the Vulnerabilities metric class. """
    def test_value(self):
        """ Test that the value is equal to the number reported by Sonar. """
        sonar = MagicMock()
        sonar.vulnerabilities = MagicMock(return_value=99)
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='sonar_id')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        metric = Vulnerabilities(subject=subject, project=project)

        result = metric.value()

        self.assertEqual(99, result)
        self.assertEqual('Hoeveelheid vulnerabilities', metric.name)
        self.assertEqual('vulnerabilities', metric.unit)
        self.assertEqual(0, metric.target_value)
        self.assertEqual(3, metric.low_target_value)
        sonar.vulnerabilities.assert_called_once_with('sonar_id')


class CodeSmellsTest(unittest.TestCase):
    """ Unit tests for the CodeSmells metric class. """
    def test_value(self):
        """ Test that the value is equal to the number reported by Sonar. """
        sonar = MagicMock()
        sonar.code_smells = MagicMock(return_value=99)
        subject = MagicMock()
        subject.metric_source_id = MagicMock(return_value='sonar_id')
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        metric = CodeSmells(subject=subject, project=project)

        result = metric.value()

        self.assertEqual(99, result)
        self.assertEqual('Hoeveelheid code smells', metric.name)
        self.assertEqual('code smells', metric.unit)
        self.assertEqual(25, metric.target_value)
        self.assertEqual(50, metric.low_target_value)
        sonar.code_smells.assert_called_once_with('sonar_id')
