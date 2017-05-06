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

from ... import metric_source
from ...domain import LowerIsBetterMetric, MetricSourceAgeMetric
from hqlib.typing import MetricParameters


class FailingRegressionTests(LowerIsBetterMetric):
    """ Metric for measuring the number of regression tests that fail. """

    name = 'Hoeveelheid falende regressietesten'
    unit = 'regressietesten'
    norm_template = 'Alle {unit} slagen.'
    perfect_template = 'Alle {tests} {unit} van {name} slagen.'
    template = '{value} van de {tests} {unit} van {name} slagen niet.'
    target_value = 0
    low_target_value = 0
    metric_source_class = metric_source.TestReport

    def value(self):
        if self._missing():
            return -1
        else:
            urls = self._get_metric_source_ids()
            return self._metric_source.failed_tests(*urls) + self._metric_source.skipped_tests(*urls)

    def _missing(self) -> bool:
        if not self._metric_source:
            return True
        urls = self._get_metric_source_ids()
        passed = self._metric_source.passed_tests(*urls)
        failed = self._metric_source.failed_tests(*urls)
        skipped = self._metric_source.skipped_tests(*urls)
        return None in (passed, failed, skipped) or passed < 0 or failed < 0 or skipped < 0

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['tests'] = '?' if self._missing() else \
            self.value() + self._metric_source.passed_tests(*self._get_metric_source_ids())
        return parameters


class RegressionTestAge(MetricSourceAgeMetric):
    """ Metric for measuring the number of days since the regression test last ran. """

    name = 'Regressietestleeftijd'
    norm_template = 'De regressietest is maximaal {target} {unit} geleden gedraaid. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De regressietest van {name} is vandaag gedraaid.'
    template = 'De regressietest van {name} is {value} {unit} geleden gedraaid.'
    metric_source_class = metric_source.TestReport
