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
        self.assertEqual('Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.', metric.norm_template)
        self.assertEqual('{name} heeft {value} {unit}.', metric.template)
        self.assertEqual(0, metric.target_value)
        self.assertEqual(3, metric.low_target_value)
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
        self.assertEqual('Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.', metric.norm_template)
        self.assertEqual('{name} heeft {value} {unit}.', metric.template)
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
        self.assertEqual('Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.', metric.norm_template)
        self.assertEqual('{name} heeft {value} {unit}.', metric.template)
        self.assertEqual(25, metric.target_value)
        self.assertEqual(50, metric.low_target_value)
        sonar.code_smells.assert_called_once_with('sonar_id')
