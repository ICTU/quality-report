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


from hqlib import domain, metric_source
from .base_performance_metric import PerformanceMetricMixin


class PerformanceLoadTestAge(PerformanceMetricMixin, domain.MetricSourceAgeMetric):
    """ Metric for measuring the age of the performance load test. """

    target_value = 3
    low_target_value = 7
    name = 'Performanceloadtestleeftijd'
    norm_template = 'De performanceloadtest is maximaal {target} {unit} geleden gedraaid. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De performanceloadtest van {name} is vandaag gedraaid.'
    template = 'De performanceloadtest van {name} is {value} {unit} geleden gedraaid.'
    metric_source_class = metric_source.PerformanceLoadTestReport


class PerformanceEnduranceTestAge(PerformanceMetricMixin, domain.MetricSourceAgeMetric):
    """ Metric for measuring the age of the performance endurance test. """

    target_value = 7
    low_target_value = 14
    name = 'Performanceduurtestleeftijd'
    norm_template = 'De performanceduurtest is maximaal {target} {unit} geleden gedraaid. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De performanceduurtest van {name} is vandaag gedraaid.'
    template = 'De performanceduurtest van {name} is {value} {unit} geleden gedraaid.'
    metric_source_class = metric_source.PerformanceEnduranceTestReport


class PerformanceScalabilityTestAge(PerformanceMetricMixin, domain.MetricSourceAgeMetric):
    """ Metric for measuring the age of the performance scalability test. """

    target_value = 7
    low_target_value = 14
    name = 'Performanceschaalbaarheidstestleeftijd'
    norm_template = 'De performanceschaalbaarheidstest is maximaal {target} {unit} geleden gedraaid. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De performanceschaalbaarheidstest van {name} is vandaag gedraaid.'
    template = 'De performanceschaalbaarheidstest van {name} is {value} {unit} geleden gedraaid.'
    metric_source_class = metric_source.PerformanceScalabilityTestReport
