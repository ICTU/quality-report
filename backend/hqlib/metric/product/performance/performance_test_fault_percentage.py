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

from typing import List

from hqlib import domain, metric_source
from hqlib.typing import MetricValue
from .base_performance_metric import PerformanceMetricMixin


class PerformanceTestFaultPercentage(PerformanceMetricMixin, domain.LowerIsBetterMetric):
    """ Metric for measuring the percentage of failed transactions in the performance test. """

    target_value = 5
    low_target_value = 10
    unit = "%"
    applicable_metric_source_classes: List[domain.MetricSource] = []  # Subclass responsibility

    def is_applicable(self) -> bool:
        return self._metric_source.__class__ in self.applicable_metric_source_classes if self._metric_source else True

    def value(self) -> MetricValue:
        if not self._metric_source:
            return -1
        return round(self._metric_source.fault_percentage(self._metric_source_id), 2)


class PerformanceLoadTestFaultPercentage(PerformanceTestFaultPercentage):
    """ Metric for measuring the percentage of failed transactions in the performance load test. """

    name = 'Performanceloadtestfoutpercentage'
    norm_template = 'Het percentage gefaalde transacties in de performanceloadtest is minder dan {target}{unit}. ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = 'Het percentage gefaalde transacties in de performanceloadtest van {name} is {value}{unit}.'
    metric_source_class = metric_source.PerformanceLoadTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceLoadTestReport]


class PerformanceEnduranceTestFaultPercentage(PerformanceTestFaultPercentage):
    """ Metric for measuring the percentage of failed transactions in the performance endurance test. """

    name = 'Performanceduurtestfoutpercentage'
    norm_template = 'Het percentage gefaalde transacties in de performanceduurtest is minder dan {target}{unit}. ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = 'Het percentage gefaalde transacties in de performanceduurtest van {name} is {value}{unit}.'
    metric_source_class = metric_source.PerformanceEnduranceTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceEnduranceTestReport]


class PerformanceScalabilityTestFaultPercentage(PerformanceTestFaultPercentage):
    """ Metric for measuring the percentage of failed transactions in the performance scalability test. """

    name = 'Performanceschaalbaarheidstestfoutpercentage'
    norm_template = 'Het percentage gefaalde transacties in de performanceschaalbaarheidstest is minder dan ' \
                    '{target}{unit}. Meer dan {low_target}{unit} is rood.'
    template = 'Het percentage gefaalde transacties in de performanceschaalbaarheidstest van {name} is {value}{unit}.'
    metric_source_class = metric_source.PerformanceScalabilityTestReport
    applicable_metric_source_classes = [metric_source.ICTUPerformanceScalabilityTestReport]
