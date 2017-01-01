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
from __future__ import absolute_import

import datetime

from ... import metric_source
from ...domain import HigherIsBetterMetric, LowerIsBetterMetric


class _RegressionTestMetric(LowerIsBetterMetric):
    """ Base class for regression test metrics. """
    metric_source_classes = (metric_source.TestReport,)

    def value(self):
        raise NotImplementedError  # pragma: no cover

    def _metric_source_ids(self):
        ids = self._metric_source_id if isinstance(self._metric_source_id, list) else [self._metric_source_id]
        return [id_ for id_ in ids if id_]


class FailingRegressionTests(_RegressionTestMetric):
    """ Metric for measuring the number of regression tests that fail. """

    name = 'Hoeveelheid falende regressietesten'
    unit = 'regressietesten'
    norm_template = 'Alle {unit} slagen.'
    perfect_template = 'Alle {tests} {unit} van {name} slagen.'
    template = '{value} van de {tests} {unit} van {name} slagen niet.'
    target_value = 0
    low_target_value = 0

    def value(self):
        if self._missing():
            return -1
        else:
            urls = self._metric_source_ids()
            return self._metric_source.failed_tests(*urls) + self._metric_source.skipped_tests(*urls)

    def _missing(self):
        urls = self._metric_source_ids()
        return self._metric_source.passed_tests(*urls) < 0 or self._metric_source.failed_tests(*urls) < 0 or \
            self._metric_source.skipped_tests(*urls) < 0

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingRegressionTests, self)._parameters()
        passed_tests = self._metric_source.passed_tests(*self._metric_source_ids())
        parameters['tests'] = '?' if self._missing() else self.value() + passed_tests
        return parameters


class RegressionTestAge(_RegressionTestMetric):
    """ Metric for measuring the number of days since the regression test last ran. """

    name = 'Regressietestleeftijd'
    unit = 'dagen'
    norm_template = 'De regressietest is maximaal {target} {unit} geleden gedraaid. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De regressietest van {name} is vandaag gedraaid.'
    template = 'De regressietest van {name} is {value} {unit} geleden gedraaid.'
    target_value = 3
    low_target_value = 7

    def value(self):
        return -1 if self._missing() else \
            (datetime.datetime.now() - self._metric_source.report_datetime(*self._metric_source_ids())).days

    def _missing(self):
        return self._metric_source.report_datetime(*self._metric_source_ids()) in (None, datetime.datetime.min)


class _ARTCoverage(HigherIsBetterMetric):
    """ Metric for measuring the coverage of automated regression tests (ART) for a product. """
    unit = '%'
    norm_template = 'Minimaal {target}{unit} van de {covered_items} wordt gedekt door geautomatiseerde ' \
                    'functionele tests en de coverage meting is niet ouder dan {old_age}. Minder dan ' \
                    '{low_target}{unit} of meting ouder dan {max_old_age} is rood.'
    template = '{name} ART {covered_item} coverage is {value}{unit} ({date}, {age} geleden).'
    perfect_value = 100
    old_age = datetime.timedelta(hours=3 * 24)
    max_old_age = datetime.timedelta(hours=5 * 24)
    metric_source_classes = [metric_source.CoverageReport]
    covered_items = covered_item = 'Subclass responsibility'

    @classmethod
    def norm_template_default_values(cls):
        values = super(_ARTCoverage, cls).norm_template_default_values()
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

    def _date(self):
        """ Return the date of the last coverage measurement from the coverage report. """
        return datetime.datetime.min if self._metric_source_id is None else \
            self._metric_source.coverage_date(self._metric_source_id)

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(_ARTCoverage, self)._parameters()
        parameters['covered_items'] = self.covered_items
        parameters['covered_item'] = self.covered_item
        return parameters


class ARTStatementCoverage(_ARTCoverage):
    """ Metric for measuring the statement coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test statement coverage'
    target_value = 80
    low_target_value = 70
    covered_item = 'statement'
    covered_items = 'statements'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.statement_coverage(self._metric_source_id)


class ARTBranchCoverage(_ARTCoverage):
    """ Metric for measuring the branch coverage of automated regression tests (ART) for a product. """

    name = 'Automatic regression test branch coverage'
    target_value = 75
    low_target_value = 60
    covered_item = 'branch'
    covered_items = 'branches'

    def _get_coverage_from_metric_source(self, metric_source_id):
        return self._metric_source.branch_coverage(self._metric_source_id)
