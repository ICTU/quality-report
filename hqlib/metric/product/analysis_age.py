"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

from typing import List

from ..metric_source_mixin import SonarDashboardMetric
from ... import metric_source
from ...domain import MetricSourceAgeMetric


class SonarAnalysisAge(SonarDashboardMetric, MetricSourceAgeMetric):
    """ Metric to measure the age of the latest Sonar analysis. """

    name = 'Leeftijd van de meest recente Sonar analyse'
    norm_template = 'De meest recente Sonar analyse is maximaal {target} {unit} oud. ' \
                    'Meer dan {low_target} {unit} is rood.'
    template = 'De meest recente Sonar analyse van {name} is {value} {unit} oud.'
    target_value = 6 * 7
    low_target_value = 9 * 7

    def _get_metric_source_ids(self) -> List[str]:
        return [self._sonar_id()]


class OWASPDependencyReportAge(MetricSourceAgeMetric):
    """ Metric to measure the age of the OWASP dependency checker report. """

    name = 'Leeftijd van het OWASP dependency rapport'
    norm_template = 'De leeftijd van het OWASP dependency rapport is maximaal {target} {unit} oud. ' \
                    'Meer dan {low_target} {unit} is rood.'
    template = 'Het meest recente OWASP dependency rapport van {name} is {value} {unit} oud.'
    metric_source_class = metric_source.OWASPDependencyReport


class OpenVASScanReportAge(MetricSourceAgeMetric):
    """ Metric to measure the age of the Open VAS Scan report. """

    name = 'Leeftijd van het Open VAS Scan rapport'
    norm_template = 'De leeftijd van het Open VAS Scan rapport is maximaal {target} {unit} oud. ' \
                    'Meer dan {low_target} {unit} is rood.'
    template = 'Het meest recente Open VAS Scan rapport van {name} is {value} {unit} oud.'
    metric_source_class = metric_source.OpenVASScanReport
