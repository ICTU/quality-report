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
from ... import metric_info
from ...domain import HigherIsBetterMetric


class IntegrationtestMetricMixin(SonarDashboardMetricMixin):
    """ Mixin class for Sonar metrics about integration tests. """

    @staticmethod
    def product_has_sonar_id(sonar, product):
        integration_test_sonar_info = metric_info.SonarProductInfo(sonar, product.integration_tests())
        return product.integration_tests() and integration_test_sonar_info.sonar_id()

    def _sonar_id(self):
        integration_test_sonar_info = metric_info.SonarProductInfo(self._sonar, self._subject.integration_tests())
        return integration_test_sonar_info.sonar_id()


class IntegrationtestCoverage(IntegrationtestMetricMixin, HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring coverage of integration tests for a product. """

    perfect_value = 100
    quality_attribute = TEST_COVERAGE

    def value(self):
        raise NotImplementedError  # pragma: no cover


class IntegrationtestLineCoverage(IntegrationtestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the line coverage of integration tests for a product. """

    name = 'Integratietest broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}% van de regels code wordt gedekt door integratietests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} integratietest line coverage is {value:.0f}%.'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._sonar.integration_test_line_coverage(self._sonar_id()))


class IntegrationtestBranchCoverage(IntegrationtestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the branch coverage of integration tests for a product. """

    name = 'Integratietest broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}% van de code branches wordt gedekt door integratietests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} integratietest branch coverage is {value:.0f}%.'
    target_value = 60
    low_target_value = 50

    def value(self):
        return round(self._sonar.integration_test_branch_coverage(self._sonar_id()))
