"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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
from ... import metric_source
from ...domain import HigherIsBetterMetric, MetricSourceAgeMetric


class AggregatedTestCoverage(HigherIsBetterMetric):
    """ Metric for measuring the aggregated coverage of different tests for a product. """
    unit = '%'
    norm_template = 'Minimaal {target}{unit} van de {covered_items} wordt gedekt door geautomatiseerde ' \
                    'tests. Minder dan {low_target}{unit} is rood.'
    template = '{name} geaggregeerde {covered_item} coverage is {value}{unit}.'
    perfect_value = 100
    metric_source_class = metric_source.AggregatedCoverageReport
    covered_items = covered_item = 'Subclass responsibility'

    @classmethod
    def norm_template_default_values(cls):
        values = super(AggregatedTestCoverage, cls).norm_template_default_values()
        values['covered_items'] = cls.covered_items
        values['covered_item'] = cls.covered_item
        return values

    def value(self):
        return int(round(self._get_coverage_from_metric_source(self._metric_source_id))) if self._metric_source else -1

    def _get_coverage_from_metric_source(self, metric_source_id):
        """ Get the actual coverage measurement from the metric source. """
        raise NotImplementedError

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['covered_items'] = self.covered_items
        parameters['covered_item'] = self.covered_item
        return parameters


class AggregatedTestStatementCoverage(AggregatedTestCoverage):
    """ Metric for measuring the statement coverage of aggregated tests for a product. """

    name = 'Geaggregeerde test statement coverage'
    target_value = 90
    low_target_value = 80
    covered_item = 'statement'
    covered_items = 'statements'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.statement_coverage(self._metric_source_id)


class AggregatedTestBranchCoverage(AggregatedTestCoverage):
    """ Metric for measuring the branch coverage of aggregated tests for a product. """

    name = 'Geaggregeerde test branch coverage'
    target_value = 85
    low_target_value = 75
    covered_item = 'branch'
    covered_items = 'branches'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.branch_coverage(self._metric_source_id)


class AggregatedTestCoverageReportAge(MetricSourceAgeMetric):
    """ Metric for measuring the number of days since the coverage report was last generated. """
    name = 'Geaggregeerde-coveragerapportageleeftijd'
    norm_template = 'De geaggregeerde coveragerapportage is maximaal {target} {unit} geleden gemaakt. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De geaggregeerde coveragerapportage van {name} is vandaag gemaakt.'
    template = 'De geaggregeerde coveragerapportage van {name} is {value} {unit} geleden gemaakt.'
    metric_source_class = metric_source.AggregatedCoverageReport
