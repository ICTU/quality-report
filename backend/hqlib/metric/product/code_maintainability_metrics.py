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

# pylint: disable=abstract-method

from hqlib import utils
from ..metric_source_mixin import SonarDashboardMetric
from ...domain import LowerIsBetterMetric


class CodeMaintainabilityMetric(SonarDashboardMetric, LowerIsBetterMetric):
    """ Abstract class for metric measuring the amount of bugs reported by Sonar. """
    norm_template = 'Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood.'
    template = '{name} heeft {value} {unit}.'
    violation_type = 'Subclass responsibility'

    extra_info_headers = {"severity": "Severity",
                          "number": "Aantal__detail-column-number",
                          "debt": "Geschatte oplostijd__detail-column-number"}

    def _metric_source_number_of_issues(self, product: str) -> int:
        """ Placeholder for metric source function """
        raise NotImplementedError

    def extra_info_rows(self) -> list((object, int)):
        """ Returns formatted rows of extra info table for code maintainability metrics. """
        severities = ['Blocker', 'Critical', 'Major', 'Minor', 'Info']
        ret = list()
        for severity in severities:
            url, count, effort = \
                self._metric_source.violations_type_severity(self._metric_source_id, self.violation_type, severity)
            ret.append((utils.format_link_object(url, severity), count, effort))
        return ret

    def value(self):
        """ Retrieves the number of issues detected by sonar. """
        val = self._metric_source_number_of_issues(self._sonar_id()) if self._metric_source else -1
        if val <= 0:
            self.extra_info_headers = None
        return val


class MaintainabilityBugs(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of bugs reported by Sonar. """
    name = 'Hoeveelheid maintainability bugs'
    unit = 'maintainability bugs'
    target_value = 0
    low_target_value = 3
    violation_type = 'BUG'
    url_label_text = 'Maintainability bugs per severity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._metric_source:
            self._metric_source_number_of_issues = self._metric_source.maintainability_bugs


class Vulnerabilities(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of vulnerabilities reported by Sonar. """
    name = 'Hoeveelheid vulnerabilities'
    unit = 'vulnerabilities'
    target_value = 0
    low_target_value = 3
    violation_type = 'VULNERABILITY'
    url_label_text = 'Vulnerabilities per severity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._metric_source:
            self._metric_source_number_of_issues = self._metric_source.vulnerabilities


class CodeSmells(CodeMaintainabilityMetric):
    """ Metric for measuring the amount of code smells reported by Sonar. """
    name = 'Hoeveelheid code smells'
    unit = 'code smells'
    target_value = 25
    low_target_value = 50
    violation_type = 'CODE_SMELL'
    url_label_text = 'Code smells per severity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._metric_source:
            self._metric_source_number_of_issues = self._metric_source.code_smells
