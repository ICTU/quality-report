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
from ..quality_attributes import TEST_COVERAGE
from ...domain import HigherIsBetterMetric


class UnitAndIntegrationTestMetricMixin(SonarDashboardMetricMixin):
    """ Mixin class for Sonar metrics about combined unit and integration tests. """

    @classmethod
    def can_be_measured(cls, product, project):
        return super(UnitAndIntegrationTestMetricMixin, cls).can_be_measured(product, project) and \
               product.unittests() and product.integration_tests()


class UnitAndIntegrationTestCoverage(UnitAndIntegrationTestMetricMixin, HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring combined coverage of unit and integration tests for a product. """

    unit = '%'
    perfect_value = 100
    quality_attribute = TEST_COVERAGE

    def value(self):
        raise NotImplementedError  # pragma: no cover


class UnitAndIntegrationTestLineCoverage(UnitAndIntegrationTestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the combined line coverage of unit and integration tests for a product. """

    name = 'Gecombineerde unit- en integratietest broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}{unit} van de regels code wordt gedekt door unit- en integratietests samen. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} gecombineerde unit- en integratietest line coverage is {value:.0f}{unit}.'
    target_value = 98
    low_target_value = 90

    def value(self):
        return round(self._sonar.overall_test_line_coverage(self._sonar_id()))


class UnitAndIntegrationTestBranchCoverage(UnitAndIntegrationTestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the combined branch coverage of unit and integration tests for a product. """

    name = 'Overall est broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}{unit} van de code branches wordt gedekt door unit- en integratietests samen. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} gecombineerde unit- en integratietest branch coverage is {value:.0f}{unit}.'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._sonar.overall_test_branch_coverage(self._sonar_id()))
