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


from ... import domain, metric_source


class UnittestCoverage(domain.HigherIsBetterMetric):  # pylint: disable=too-few-public-methods
    """ Base class for metrics measuring coverage of unit tests for a product. """

    unit = '%'
    perfect_value = 100
    metric_source_class = metric_source.UnittestCoverageReport

    def value(self):
        raise NotImplementedError


class UnittestLineCoverage(UnittestCoverage):
    """ Metric for measuring the line coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (line coverage)'
    norm_template = 'Minimaal {target}{unit} van de regels code wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest line coverage is {value:.0f}{unit}.'
    target_value = 98
    low_target_value = 90

    def value(self):
        return round(self._metric_source.statement_coverage(self._metric_source_id)) if self._metric_source else -1


class UnittestBranchCoverage(UnittestCoverage):
    """ Metric for measuring the branch coverage of unit tests for a product. """

    name = 'Unit test broncode dekking (branch coverage)'
    norm_template = 'Minimaal {target}{unit} van de code branches wordt gedekt door unittests. ' \
        'Lager dan {low_target}{unit} is rood.'
    template = '{name} unittest branch coverage is {value:.0f}{unit}.'
    target_value = 80
    low_target_value = 60

    def value(self):
        return round(self._metric_source.branch_coverage(self._metric_source_id)) if self._metric_source else -1
