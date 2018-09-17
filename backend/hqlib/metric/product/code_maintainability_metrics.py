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


from ..metric_source_mixin import SonarDashboardMetric
from ...domain import LowerIsBetterMetric


class CodeMaintainabilityMetric(SonarDashboardMetric, LowerIsBetterMetric):
    """ Abstract class for metric measuring the amount of bugs reported by Sonar. """
    norm_template = 'Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.'
    template = '{name} heeft {value} {unit}.'


class MaintainabilityBugs(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of bugs reported by Sonar. """
    name = 'Hoeveelheid maintainability bugs'
    unit = 'maintainability bugs'
    target_value = 0
    low_target_value = 3

    def value(self):
        """ Retrieves the number of maintainability bugs detected by sonar qube. """
        return self._metric_source.maintainability_bugs(self._sonar_id()) if self._metric_source else -1


class Vulnerabilities(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of vulnerabilities reported by Sonar. """
    name = 'Hoeveelheid vulnerabilities'
    unit = 'vulnerabilities'
    target_value = 0
    low_target_value = 3

    def value(self):
        """ Retrieves the number of vulnerabilities detected by sonar qube. """
        return self._metric_source.vulnerabilities(self._sonar_id()) if self._metric_source else -1


class CodeSmells(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of code smells reported by Sonar. """
    name = 'Hoeveelheid code smells'
    unit = 'code smells'
    target_value = 25
    low_target_value = 50

    def value(self):
        """ Retrieves the number of code smells detected by sonar qube. """
        return self._metric_source.code_smells(self._sonar_id()) if self._metric_source else -1
