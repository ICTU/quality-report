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

from ..metric_source_mixin import SonarDashboardMetricMixin
from ..quality_attributes import TEST_COVERAGE, TEST_QUALITY
from ... import metric_info
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class UnittestMetricMixin(SonarDashboardMetricMixin):
    """ Mixin class for Sonar metrics about unit tests. """

    @staticmethod
    def product_has_sonar_id(sonar, product):
        unittest_sonar_info = metric_info.SonarProductInfo(sonar, product.unittests())
        return product.unittests() and not product.integration_tests() and unittest_sonar_info.sonar_id()

    def _parameters(self):
        """ Add the number of unit tests to the parameters for the report. """
        # pylint: disable=protected-access
        parameters = super(UnittestMetricMixin, self)._parameters()
        parameters['tests'] = self._sonar.unittests(self._sonar_id())
        return parameters

    def _sonar_id(self):
        unittest_sonar_info = metric_info.SonarProductInfo(self._sonar, self._subject.unittests())
        return unittest_sonar_info.sonar_id()


class FailingUnittests(UnittestMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of unit tests that fail. """

    name = 'Falende unittesten'
    unit = 'unittesten'
    norm_template = 'Alle unittesten slagen.'
    perfect_template = '{tests} van de {tests} {unit} slagen.'
    template = '{value} van de {tests} {unit} falen.'
    target_value = 0
    low_target_value = 0
    quality_attribute = TEST_QUALITY

    def value(self):
        return self._sonar.failing_unittests(self._sonar_id())

    def status(self):
        status = super(FailingUnittests, self).status()
        # Don't report 0 failing unit tests out of 0 unit tests as perfect but rather as red:
        return 'red' if status == 'perfect' and self._sonar.unittests(self._sonar_id()) == 0 else status


class UnittestCoverage(UnittestMetricMixin, HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring coverage of unit tests for a product. """

    unit = '%'
    perfect_value = 100
    quality_attribute = TEST_COVERAGE

    def value(self):
        raise NotImplementedError  # pragma: no cover


class UnittestLineCoverage(UnittestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the line coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}{unit} van de regels code wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest line coverage is {value:.0f}{unit} ({tests} unittests).'
    target_value = 98
    low_target_value = 90

    def value(self):
        return round(self._sonar.unittest_line_coverage(self._sonar_id()))


class UnittestBranchCoverage(UnittestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the branch coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}{unit} van de code branches wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest branch coverage is {value:.0f}{unit} ({tests} unittests).'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._sonar.unittest_branch_coverage(self._sonar_id()))
