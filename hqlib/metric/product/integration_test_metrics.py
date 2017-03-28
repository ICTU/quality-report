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


from ..metric_source_mixin import SonarDashboardMetric
from ...domain import HigherIsBetterMetric


class IntegrationtestMetricMixin(SonarDashboardMetric):  # pylint: disable=too-few-public-methods
    """ Mixin class for Sonar metrics about integration tests. """

    @classmethod
    def is_applicable(cls, product):
        """ Return whether the integration test metric is applicable to the product. This is only the case if the
            product has integration tests, but no unit tests, because if it does, the combined unit and integration
            test metrics will be used. """
        return product.has_integration_tests() and not product.has_unittests()


class IntegrationtestCoverage(IntegrationtestMetricMixin, HigherIsBetterMetric):
    """ Base class for metrics measuring coverage of integration tests for a product. """

    unit = '%'
    perfect_value = 100

    def value(self):
        raise NotImplementedError  # pragma: no cover


class IntegrationtestLineCoverage(IntegrationtestCoverage):
    """ Metric for measuring the line coverage of integration tests for a product. """

    name = 'Integratietest broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}{unit} van de regels code wordt gedekt door integratietests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} integratietest line coverage is {value:.0f}{unit}.'
    target_value = 98
    low_target_value = 90

    def value(self):
        coverage = self._metric_source.integration_test_line_coverage(self._sonar_id())
        return -1 if coverage is None else round(coverage)


class IntegrationtestBranchCoverage(IntegrationtestCoverage):
    """ Metric for measuring the branch coverage of integration tests for a product. """

    name = 'Integratietest broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}{unit} van de code branches wordt gedekt door integratietests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} integratietest branch coverage is {value:.0f}{unit}.'
    target_value = 80
    low_target_value = 60

    def value(self):
        coverage = self._metric_source.integration_test_branch_coverage(self._sonar_id())
        return -1 if coverage is None else round(coverage)
