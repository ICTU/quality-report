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
from ...domain import LowerPercentageIsBetterMetric


class Duplication(SonarDashboardMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of duplicated lines of code. """

    name = 'Duplicatie van broncode'
    target_value = 0
    low_target_value = 4
    norm_template = 'Maximaal {target}% gedupliceerde regels code. Meer dan {low_target}% is rood.'
    template = '{name} heeft {value}% ({numerator} op {denominator}) duplicatie.'

    def _numerator(self) -> int:
        return self._metric_source.duplicated_lines(self._sonar_id()) if self._metric_source else -1

    def _denominator(self) -> int:
        return self._metric_source.lines(self._sonar_id()) if self._metric_source else -1


class JavaDuplication(Duplication):  # pylint: disable=too-many-ancestors
    """ Metric for measuring the percentage of duplicated lines of code in Java code. """
    pass  # For backwards compatibility
