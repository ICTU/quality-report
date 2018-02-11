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


from typing import List

from hqlib.typing import MetricParameters
from ..metric_source_mixin import SonarDashboardMetric, SonarViolationsMetric, SonarMetric
from ...domain import LowerIsBetterMetric


class Violations(SonarDashboardMetric, LowerIsBetterMetric):
    """ Metric for measuring the amount of violations reported by Sonar. """
    unit = 'violations'
    norm_template = 'Maximaal {target} {violation_type} {unit}. ' \
        'Meer dan {low_target} {violation_type} {unit} is rood.'
    template = '{name} heeft {value} {violation_type} {unit}.'
    violation_type = 'Subclass responsibility'

    @classmethod
    def norm_template_default_values(cls):
        values = super(Violations, cls).norm_template_default_values()
        values['violation_type'] = cls.violation_type
        return values

    def value(self):
        method_name = '{0}_violations'.format(self.violation_type)
        return getattr(self._metric_source, method_name)(self._sonar_id()) if self._metric_source else -1

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['violation_type'] = self.violation_type
        return parameters


class BlockerViolations(Violations):
    """ Metric for measuring the number of blocker violations reported by Sonar. """

    name = 'Hoeveelheid blocker violations'
    violation_type = 'blocker'
    target_value = 0
    low_target_value = 0


class CriticalViolations(Violations):
    """ Metric for measuring the number of critical violations reported by Sonar. """

    name = 'Hoeveelheid critical violations'
    violation_type = 'critical'
    target_value = 0
    low_target_value = 1


class MajorViolations(Violations):
    """ Metric for measuring the number of major violations reported by Sonar. """

    name = 'Hoeveelheid major violations'
    violation_type = 'major'
    target_value = 25
    low_target_value = 50


class NoSonar(SonarViolationsMetric, LowerIsBetterMetric):
    """ Metric for measuring the number of times //NOSONAR is used to suppress violations. """
    name = 'Hoeveelheid violation-onderdrukkingen met //NOSONAR'
    unit = 'violation-onderdrukkingen'
    norm_template = 'Violations worden maximaal {target} keer onderdrukt met //NOSONAR. ' \
        'Meer dan {low_target} {unit} is rood.'
    template = '{name} bevat {value} {unit}.'
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._metric_source.no_sonar(self._sonar_id()) if self._metric_source else -1


class FalsePositives(SonarMetric, LowerIsBetterMetric):
    """ Metric for measuring the number of issues marked as false positive. """
    name = 'Hoeveelheid false positives'
    unit = 'false positives'
    norm_template = 'Maximaal {target} violations zijn gemarkeerd als false positive. ' \
                    'Meer dan {low_target} {unit} is rood.'
    template = '{name} bevat {value} violations die zijn gemarkeerd als false positive.'
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._metric_source.false_positives(self._sonar_id()) if self._metric_source else -1

    def _metric_source_urls(self) -> List[str]:
        """ Return the url to the Sonar violations. """
        return [self._metric_source.false_positives_url(self._sonar_id())] if self._metric_source else []
