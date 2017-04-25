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

from ... import metric_source
from ...domain import HigherIsBetterMetric, MetricSourceAgeMetric
from hqlib.typing import MetricParameters


class ARTCoverage(HigherIsBetterMetric):
    """ Metric for measuring the coverage of automated regression tests (ART) for a product. """
    unit = '%'
    norm_template = 'Minimaal {target}{unit} van de {covered_items} wordt gedekt door geautomatiseerde ' \
                    'functionele tests. Minder dan {low_target}{unit} is rood.'
    template = '{name} ART {covered_item} coverage is {value}{unit}.'
    perfect_value = 100
    metric_source_class = metric_source.CoverageReport
    covered_items = covered_item = 'Subclass responsibility'

    @classmethod
    def norm_template_default_values(cls):
        values = super(ARTCoverage, cls).norm_template_default_values()
        values['covered_items'] = cls.covered_items
        values['covered_item'] = cls.covered_item
        return values

    def value(self):
        if self._metric_source_id is None:
            return -1
        coverage = self._get_coverage_from_metric_source(self._metric_source_id)
        return -1 if coverage is None else int(round(coverage))

    def _get_coverage_from_metric_source(self, metric_source_id):
        """ Get the actual coverage measurement from the metric source. """
        raise NotImplementedError  # pragma: nocover

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['covered_items'] = self.covered_items
        parameters['covered_item'] = self.covered_item
        return parameters


class ARTStatementCoverage(ARTCoverage):
    """ Metric for measuring the statement coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test statement coverage'
    target_value = 80
    low_target_value = 70
    covered_item = 'statement'
    covered_items = 'statements'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.statement_coverage(self._metric_source_id)


class ARTBranchCoverage(ARTCoverage):
    """ Metric for measuring the branch coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test branch coverage'
    target_value = 75
    low_target_value = 60
    covered_item = 'branch'
    covered_items = 'branches'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.branch_coverage(self._metric_source_id)


class CoverageReportAge(MetricSourceAgeMetric):
    """ Metric for measuring the number of days since the coverage report was last generated. """
    name = 'Coveragerapportageleeftijd'
    norm_template = 'De coveragerapportage is maximaal {target} {unit} geleden gemaakt. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De coveragerapportage van {name} is vandaag gemaakt.'
    template = 'De coveragerapportage van {name} is {value} {unit} geleden gemaakt.'
    metric_source_class = metric_source.CoverageReport
