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
        return product.unittests() and unittest_sonar_info.sonar_id()

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

    name = 'Falende unit testen'
    norm_template = 'Alle unittests slagen.'
    perfect_template = '{passed_tests} van de {tests} unittests slagen. '
    template = '{value} van de {tests} unittests falen.'
    target_value = 0
    low_target_value = 0
    quality_attribute = TEST_QUALITY

    def value(self):
        return self._sonar.failing_unittests(self._sonar_id())

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else super(FailingUnittests, self)._get_template()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingUnittests, self)._parameters()
        parameters['passed_tests'] = parameters['tests'] - self.value()
        return parameters


class UnittestCoverage(UnittestMetricMixin, HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring coverage of unit tests for a product. """

    perfect_value = 100
    quality_attribute = TEST_COVERAGE

    def value(self):
        raise NotImplementedError  # pragma: no cover


class UnittestLineCoverage(UnittestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the line coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}% van de regels code wordt gedekt door unittests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} unittest line coverage is {value:.0f}% ({tests} unittests).'
    target_value = 98
    low_target_value = 90

    def value(self):
        return round(self._sonar.line_coverage(self._sonar_id()))


class UnittestBranchCoverage(UnittestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the branch coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}% van de code branches wordt gedekt door unittests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} unittest branch coverage is {value:.0f}% ({tests} unittests).'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._sonar.branch_coverage(self._sonar_id()))
