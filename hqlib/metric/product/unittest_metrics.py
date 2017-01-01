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
from __future__ import absolute_import

from ..metric_source_mixin import SonarDashboardMetricMixin
from ... import metric_info
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class UnittestMetricMixin(SonarDashboardMetricMixin):
    """ Mixin class for Sonar metrics about unit tests. """

    @classmethod
    def is_applicable(cls, product):
        """ Return whether the unit test metric is applicable to the product. This is only the case if the product
            has no integration tests, because if it does, the combined unit and integration test metrics should be
            used. """
        return not product.integration_tests()

    def _parameters(self):
        """ Add the number of unit tests to the parameters for the report. """
        # pylint: disable=protected-access
        parameters = super(UnittestMetricMixin, self)._parameters()
        parameters['tests'] = self._metric_source.unittests(self._sonar_id())
        return parameters

    def _sonar_id(self):
        unittest_sonar_info = metric_info.SonarProductInfo(self._metric_source, self._subject.unittests())
        return unittest_sonar_info.sonar_id()


class FailingUnittests(UnittestMetricMixin, LowerIsBetterMetric):
    """ Metric for measuring the number of unit tests that fail. """

    name = 'Hoeveelheid falende unittesten'
    unit = 'unittesten'
    norm_template = 'Alle unittesten slagen.'
    perfect_template = '{tests} van de {tests} {unit} slagen.'
    template = '{value} van de {tests} {unit} falen.'
    no_tests_template = 'Er zijn geen {unit}.'
    target_value = 0
    low_target_value = 0

    def value(self):
        value = self._metric_source.failing_unittests(self._sonar_id())
        return -1 if value is None else value

    def status(self):
        return 'red' if self.__no_tests() else super(FailingUnittests, self).status()

    def _get_template(self):
        return self.no_tests_template if self.__no_tests() else super(FailingUnittests, self)._get_template()

    def __no_tests(self):
        """ Return True if are no unit tests. """
        return self._metric_source.unittests(self._sonar_id()) == 0


class UnittestCoverage(UnittestMetricMixin, HigherIsBetterMetric):
    """ Base class for metrics measuring coverage of unit tests for a product. """

    unit = '%'
    perfect_value = 100

    def value(self):
        raise NotImplementedError  # pragma: no cover


class UnittestLineCoverage(UnittestCoverage):
    """ Metric for measuring the line coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}{unit} van de regels code wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest line coverage is {value:.0f}{unit} ({tests} unittests).'
    target_value = 98
    low_target_value = 90

    def value(self):
        coverage = self._metric_source.unittest_line_coverage(self._sonar_id())
        return -1 if coverage is None else round(coverage)


class UnittestBranchCoverage(UnittestCoverage):
    """ Metric for measuring the branch coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}{unit} van de code branches wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest branch coverage is {value:.0f}{unit} ({tests} unittests).'
    target_value = 80
    low_target_value = 60

    def value(self):
        coverage = self._metric_source.unittest_branch_coverage(self._sonar_id())
        return -1 if coverage is None else round(coverage)
