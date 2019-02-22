"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime
from typing import List

from hqlib import domain, metric_source
from .base_performance_metric import PerformanceMetricMixin


class PerformanceTestDuration(PerformanceMetricMixin, domain.HigherIsBetterMetric):
    """ Metric for measuring the duration of the performance test. """

    target_value = 30
    low_target_value = 20
    unit = "minuten"
    applicable_metric_source_classes: List[domain.MetricSource] = []  # Subclass responsibility

    def is_applicable(self) -> bool:
        return self._metric_source.__class__ in self.applicable_metric_source_classes if self._metric_source else True

    def value(self):
        if not self._metric_source:
            return -1
        duration = self._metric_source.duration(self._metric_source_id)
        return -1 if duration == datetime.timedelta.max else round(duration.seconds / 60.)


class PerformanceLoadTestDuration(PerformanceTestDuration):
    """ Metric for measuring the duration of the performance load test. """

    name = 'Performanceloadtestduur'
    norm_template = 'De uitvoeringstijd van de performanceloadtest is meer dan {target} {unit}. ' \
                    'Minder dan {low_target} {unit} is rood.'
    template = 'De uitvoeringstijd van de performanceloadtest van {name} is {value} {unit}.'
    metric_source_class = metric_source.PerformanceLoadTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceLoadTestReport]


class PerformanceEnduranceTestDuration(PerformanceTestDuration):
    """ Metric for measuring the duration of the performance endurance test. """

    target_value = 60 * 6
    low_target_value = 60 * 5
    name = 'Performanceduurtestduur'
    norm_template = 'De uitvoeringstijd van de performanceduurtest is meer dan {target} {unit}. ' \
                    'Minder dan {low_target} {unit} is rood.'
    template = 'De uitvoeringstijd van de performanceduurtest van {name} is {value} {unit}.'
    metric_source_class = metric_source.PerformanceEnduranceTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceEnduranceTestReport]


class PerformanceScalabilityTestDuration(PerformanceTestDuration):
    """ Metric for measuring the duration of the performance scalability test. """

    name = 'Performanceschaalbaarheidstestduur'
    norm_template = 'De uitvoeringstijd van de performanceschaalbaarheidstest is meer dan {target} {unit}. ' \
                    'Minder dan {low_target} {unit} is rood.'
    template = 'De uitvoeringstijd van de performanceschaalbaarheidstest van {name} is {value} {unit}.'
    metric_source_class = metric_source.PerformanceScalabilityTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceScalabilityTestReport]
