'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import SonarDashboardMetricMixin
from qualitylib.metric.quality_attributes import CODE_QUALITY


class Violations(SonarDashboardMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the amount of violations reported by Sonar. '''
    norm_template = 'Maximaal %(target)d %(violation_type)s violations. ' \
        'Meer dan %(low_target)d %(violation_type)s violations is rood.'
    template = '%(name)s heeft %(value)d %(violation_type)s violations.'
    quality_attribute = CODE_QUALITY
    violation_type = 'Subclass responsibility'

    @classmethod
    def can_be_measured(cls, product, project):
        return super(Violations, cls).can_be_measured(product, project) and \
            product.sonar_id()

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


class CriticalViolations(Violations):  # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of critical violations reported by 
        Sonar. '''

    name = 'Critical violations'
    violation_type = 'critical'
    target_value = 0
    low_target_value = 1

    def value(self):
        return self._sonar.critical_violations(self._sonar_id())


class MajorViolations(Violations):  # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of major violations reported by 
        Sonar. '''

    name = 'Major violations'
    violation_type = 'major'
    target_value = 25
    low_target_value = 50

    def value(self):
        return self._sonar.major_violations(self._sonar_id())
