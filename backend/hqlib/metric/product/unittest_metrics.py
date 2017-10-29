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

from hqlib.domain import LowerIsBetterMetric
from hqlib.typing import MetricParameters
from hqlib import metric_source


class FailingUnittests(LowerIsBetterMetric):
    """ Metric for measuring the number of unit tests that fail. """

    name = 'Hoeveelheid falende unittesten'
    unit = 'unittesten'
    norm_template = 'Alle unittesten slagen.'
    perfect_template = '{tests} van de {tests} {unit} slagen.'
    template = '{value} van de {tests} {unit} falen.'
    no_tests_template = 'Er zijn geen {unit}.'
    target_value = 0
    low_target_value = 0
    metric_source_class = metric_source.UnitTestReport

    def value(self):
        value = self._metric_source.failed_tests(self.__metric_source_id()) if self._metric_source else None
        return -1 if value is None else value

    def status(self) -> str:
        return 'red' if self.__nr_tests() == 0 else super().status()

    def _get_template(self) -> str:
        return self.no_tests_template if self.__nr_tests() == 0 else super()._get_template()

    def __nr_tests(self) -> int:
        """ Return the number of unit tests. """
        if self._metric_source:
            metric_source_id = self.__metric_source_id()
            return self._metric_source.passed_tests(metric_source_id) + \
                self._metric_source.failed_tests(metric_source_id) + \
                self._metric_source.skipped_tests(metric_source_id)
        else:
            return 0

    def __metric_source_id(self) -> str:
        """ Return the id of the subject in the metric source. """
        return self._subject.metric_source_id(self._metric_source) or '' \
            if (self._subject and self._metric_source) else ''

    def _parameters(self) -> MetricParameters:
        """ Add the number of unit tests to the parameters for the report. """
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['tests'] = str(self.__nr_tests()) if self._metric_source else '?'
        return parameters
