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

from hqlib.typing import MetricParameters

from ..metric_source_mixin import SonarDashboardMetric
from ...domain import HigherIsBetterMetric


class UnittestCoverage(SonarDashboardMetric, HigherIsBetterMetric):  # pylint: disable=too-few-public-methods
    """ Base class for metrics measuring coverage of unit tests for a product. """

    unit = '%'
    perfect_value = 100

    @classmethod
    def is_applicable(cls, product):
        """ Return whether the unit test metric is applicable to the product. This is only the case if the product
            has no integration tests, because if it does, the combined unit and integration test metrics should be
            used. """
        return not product.has_integration_tests()

    def value(self):
        raise NotImplementedError

    def _parameters(self) -> MetricParameters:
        """ Add the number of unit tests to the parameters for the report. """
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['tests'] = self._metric_source.unittests(self._sonar_id())
        return parameters


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
