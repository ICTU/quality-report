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


class OverallTestMetricMixin(SonarDashboardMetricMixin):
    """ Mixin class for Sonar metrics about overall tests. """

    @classmethod
    def can_be_measured(cls, product, project):
        return super(OverallTestMetricMixin, cls).can_be_measured(product, project) and \
            product.unittests() and product.integration_tests()


class OverallTestCoverage(OverallTestMetricMixin, HigherIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring overall coverage of tests for a product. """

    perfect_value = 100
    quality_attribute = TEST_COVERAGE

    def value(self):
        raise NotImplementedError  # pragma: no cover


class OverallTestLineCoverage(OverallTestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the overall line coverage of tests for a product. """

    name = 'Overall test broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}% van de regels code wordt gedekt door unit- en integratietests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} overall test line coverage is {value:.0f}%.'
    target_value = 100
    low_target_value = 80

    def value(self):
        return round(self._sonar.overall_test_line_coverage(self._sonar_id()))


class OverallTestBranchCoverage(OverallTestCoverage):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the overall branch coverage of tests for a product. """

    name = 'Overall est broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}% van de code branches wordt gedekt door unit- en integratietests. ' \
        'Lager dan {low_target}% is rood.'
    template = '{name} overall test branch coverage is {value:.0f}%.'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._sonar.overall_test_branch_coverage(self._sonar_id()))
