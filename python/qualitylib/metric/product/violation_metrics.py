"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import

from ..metric_source_mixin import SonarDashboardMetricMixin, SonarViolationsMetricMixin, SonarMetricMixin
from ..quality_attributes import CODE_QUALITY
from ...domain import LowerIsBetterMetric


class Violations(SonarDashboardMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the amount of violations reported by Sonar. """
    norm_template = 'Maximaal {target} {violation_type} violations. ' \
        'Meer dan {low_target} {violation_type} violations is rood.'
    template = '{name} heeft {value} {violation_type} violations.'
    quality_attribute = CODE_QUALITY
    violation_type = 'Subclass responsibility'

    @classmethod
    def norm_template_default_values(cls):
        values = super(Violations, cls).norm_template_default_values()
        values['violation_type'] = cls.violation_type
        return values

    def value(self):
        raise NotImplementedError  # pragma: no cover

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(Violations, self)._parameters()
        parameters['violation_type'] = self.violation_type
        return parameters


class BlockerViolations(Violations):  # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of blocker violations reported by Sonar. """

    name = 'Blocker violations'
    violation_type = 'blocker'
    target_value = 0
    low_target_value = 0

    def value(self):
        return self._sonar.blocker_violations(self._sonar_id())


class CriticalViolations(Violations):  # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of critical violations reported by Sonar. """

    name = 'Critical violations'
    violation_type = 'critical'
    target_value = 0
    low_target_value = 1

    def value(self):
        return self._sonar.critical_violations(self._sonar_id())


class MajorViolations(Violations):  # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of major violations reported by Sonar. """

    name = 'Major violations'
    violation_type = 'major'
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._sonar.major_violations(self._sonar_id())


class NoSonar(SonarViolationsMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of times //NOSONAR is used to suppress violations. """
    norm_template = 'Violations worden maximaal {target} keer onderdrukt met //NOSONAR. ' \
        'Meer dan {low_target} keer is rood.'
    template = '{name} bevat {value} keer //NOSONAR.'
    quality_attribute = CODE_QUALITY
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._sonar.no_sonar(self._sonar_id())


class FalsePositives(SonarMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of issues marked as false positive. """
    norm_template = 'Maximaal {target} violations zijn gemarkeerd als false positive. Meer dan {low_target} is rood.'
    template = '{name} bevat {value} violations die zijn gemarkeerd als false positive.'
    quality_attribute = CODE_QUALITY
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._sonar.false_positives(self._sonar_id())

    def _sonar_url(self):
        """ Return the url to the Sonar violations. """
        return self._sonar.false_positives_url(self._sonar_id())
