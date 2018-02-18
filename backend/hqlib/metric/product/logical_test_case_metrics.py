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


import datetime

from hqlib.typing import MetricParameters
from ..metric_source_mixin import BirtTestDesignMetric
from ... import metric_source, utils
from ...domain import LowerIsBetterMetric


class LogicalTestCaseMetric(BirtTestDesignMetric, LowerIsBetterMetric):
    """ Base class for metrics measuring the quality of logical test cases. """
    unit = 'logische testgevallen'

    def value(self):
        nr_ltcs, nr_ltcs_ok = self._nr_ltcs(), self._nr_ltcs_ok()
        return -1 if -1 in (nr_ltcs_ok, nr_ltcs) else nr_ltcs - nr_ltcs_ok

    def _nr_ltcs_ok(self) -> int:
        """ Return the number of logical test cases whose quality is good. """
        raise NotImplementedError

    def _nr_ltcs(self) -> int:
        """ Return the total number of logical test cases. """
        raise NotImplementedError

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['total'] = str(self._nr_ltcs())
        return parameters


class LogicalTestCasesNotReviewed(LogicalTestCaseMetric):
    """ Metric for measuring the number of logical test cases that has not been reviewed. """

    name = 'Reviewstatus van logische testgevallen'
    unit = "niet gereviewde " + LogicalTestCaseMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} logische testgevallen.'
    target_value = 0
    low_target_value = 15

    def _nr_ltcs_ok(self) -> int:
        return self._metric_source.reviewed_ltcs() if self._metric_source else -1

    def _nr_ltcs(self) -> int:
        return self._metric_source.nr_ltcs() if self._metric_source else -1


class LogicalTestCasesNotApproved(LogicalTestCaseMetric):
    """ Metric for measuring the number of logical test cases that has not been approved. """

    name = 'Goedkeuring van logische testgevallen'
    unit = "niet goedgekeurde " + LogicalTestCaseMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} gereviewde logische testgevallen.'
    target_value = 0
    low_target_value = 10

    def _nr_ltcs_ok(self) -> int:
        return self._metric_source.approved_ltcs() if self._metric_source else -1

    def _nr_ltcs(self) -> int:
        return self._metric_source.reviewed_ltcs() if self._metric_source else -1


class LogicalTestCasesNotAutomated(LogicalTestCaseMetric):
    """ Metric for measuring the number of logical test cases that should be automated that has actually been
        automated. """

    name = 'Automatisering van logische testgevallen'
    unit = "nog te automatiseren " + LogicalTestCaseMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} geautomatiseerde logische testgevallen.'
    target_value = 9
    low_target_value = 15

    def _nr_ltcs_ok(self) -> int:
        return self._metric_source.nr_automated_ltcs() if self._metric_source else -1

    def _nr_ltcs(self) -> int:
        return self._metric_source.nr_ltcs_to_be_automated() if self._metric_source else -1


class ManualLogicalTestCases(LowerIsBetterMetric):
    """ Metric for measuring how long ago the manual logical test cases have been tested. """

    name = 'Tijdige uitvoering van handmatige logische testgevallen'
    unit = 'handmatige logische testgevallen'
    norm_template = 'Alle {unit} zijn minder dan {target} dagen geleden uitgevoerd. ' \
        'Langer dan {low_target} dagen geleden is rood.'
    template = '{nr_manual_ltcs_too_old} van de {nr_manual_ltcs} {unit} zijn ' \
        'te lang geleden (meest recente {value} dag(en)) uitgevoerd.'
    never_template = 'De {nr_manual_ltcs} {unit} zijn nog niet allemaal uitgevoerd.'
    no_manual_tests_template = 'Er zijn geen {unit}.'
    target_value = 21
    low_target_value = 28
    metric_source_class = metric_source.Birt

    def value(self):
        if self._missing():
            return -1
        if self._metric_source.nr_manual_ltcs() == 0:
            return 0
        return (datetime.datetime.now() - self._metric_source.date_of_last_manual_test()).days

    def _metric_source_urls(self):
        return [self._metric_source.manual_test_execution_url()] if self._metric_source else []

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['date'] = utils.format_date(self._metric_source.date_of_last_manual_test()) \
            if self._metric_source else '?'
        parameters['nr_manual_ltcs'] = self._metric_source.nr_manual_ltcs() \
            if self._metric_source else '?'
        parameters['nr_manual_ltcs_too_old'] = self._metric_source.nr_manual_ltcs_too_old('trunk', self.target()) \
            if self._metric_source else '?'
        return parameters

    def _get_template(self) -> str:
        if self._metric_source:
            if self._metric_source.nr_manual_ltcs() == 0:
                return self.no_manual_tests_template
            elif self._metric_source.date_of_last_manual_test() == datetime.datetime.min:
                return self.never_template
        return super()._get_template()

    def _missing(self) -> bool:
        return self._metric_source.date_of_last_manual_test() == datetime.datetime.min if self._metric_source else True


class NumberOfManualLogicalTestCases(LogicalTestCaseMetric):
    """ Metric for measuring the number of manual logical test cases. """

    name = 'Hoeveelheid handmatige logische testgevallen'
    unit = "handmatige " + LogicalTestCaseMetric.unit
    template = 'Er zijn {value} {unit}, van in totaal {total} logische testgevallen.'
    target_value = 10
    low_target_value = 50

    def _nr_ltcs_ok(self) -> int:
        nr_ltcs = self._nr_ltcs()
        nr_manual_ltcs = self._metric_source.nr_manual_ltcs() if self._metric_source else -1
        return -1 if -1 in (nr_ltcs, nr_manual_ltcs) else nr_ltcs - nr_manual_ltcs

    def _nr_ltcs(self) -> int:
        return self._metric_source.nr_ltcs() if self._metric_source else -1

    def _metric_source_urls(self):
        return [self._metric_source.manual_test_execution_url()] if self._metric_source else []


class DurationOfManualLogicalTestCases(LowerIsBetterMetric):
    """ Metric for measuring how long it takes to execute the manual logical test cases. """

    name = 'Uitvoeringstijd van handmatige logische testgevallen'
    unit = 'minuten'
    norm_template = 'De uitvoering van de handmatige logische testgevallen kost maximaal {target} {unit}. ' \
                    'Meer dan {low_target} {unit} is rood.'
    template = 'De uitvoering van {measured} van de {total} handmatige logische testgevallen kost {value} {unit}.'
    target_value = 120
    low_target_value = 240
    metric_source_class = metric_source.ManualLogicalTestCaseTracker

    def value(self):
        return self._metric_source.sum_field(*self._get_metric_source_ids()) \
            if self._metric_source else -1

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        if not self._missing():
            parameters['total'] = total = self._metric_source.nr_issues(*self._get_metric_source_ids())
            not_measured = self._metric_source.nr_issues_with_field_empty(*self._get_metric_source_ids())
            parameters['measured'] = total - not_measured
        return parameters


class ManualLogicalTestCasesWithoutDuration(LowerIsBetterMetric):
    """ Metric for measuring how many of the manual test cases have not been measured for duration. """

    name = 'Hoeveelheid logische testgevallen zonder ingevulde uitvoeringstijd'
    unit = 'handmatige logische testgevallen'
    norm_template = 'Van alle {unit} is de uitvoeringstijd ingevuld. Meer dan {low_target} {unit} niet ingevuld is ' \
                    'rood.'
    template = 'Van {value} van de {total} {unit} is de uitvoeringstijd niet ingevuld.'
    target_value = 0
    low_target_value = 5
    metric_source_class = metric_source.ManualLogicalTestCaseTracker

    def value(self):
        return self._metric_source.nr_issues_with_field_empty(*self._get_metric_source_ids()) \
            if self._metric_source else -1

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['total'] = str(self._metric_source.nr_issues(*self._get_metric_source_ids())) \
            if self._metric_source else '?'
        return parameters
