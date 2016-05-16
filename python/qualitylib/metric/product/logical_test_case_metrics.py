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

import datetime

from ..metric_source_mixin import BirtMetricMixin, BirtTestDesignMetricMixin, JiraMetricMixin
from ..quality_attributes import TEST_COVERAGE, DOC_QUALITY, TEST_QUALITY
from ... import metric_source
from ...domain import LowerIsBetterMetric


class LogicalTestCaseMetric(BirtTestDesignMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics measuring the quality of logical test cases. """
    @classmethod
    def can_be_measured(cls, product, project):
        return super(LogicalTestCaseMetric, cls).can_be_measured(product, project) and not product.product_version()

    def value(self):
        return self._nr_ltcs() - self._nr_ltcs_ok()

    def _nr_ltcs_ok(self):
        """ Return the number of logical test cases whose quality is good. """
        raise NotImplementedError  # pragma: no cover

    def _nr_ltcs(self):
        """ Return the total number of logical test cases. """
        raise NotImplementedError  # pragma: no cover

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(LogicalTestCaseMetric, self)._parameters()
        parameters['total'] = self._nr_ltcs()
        return parameters


class LogicalTestCasesNotReviewed(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of logical test cases that has not been reviewed. """

    name = 'Review van logische testgevallen'
    norm_template = 'Maximaal {target} van de logische testgevallen is niet gereviewd. Meer dan {low_target} is rood.'
    template = '{name} heeft {value} niet gereviewde logische testgevallen van in totaal {total} logische testgevallen.'
    target_value = 0
    low_target_value = 15
    quality_attribute = DOC_QUALITY

    def _nr_ltcs_ok(self):
        return self._birt.reviewed_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.nr_ltcs(self._birt_id())


class LogicalTestCasesNotApproved(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of logical test cases that has not been approved. """

    name = 'Goedkeuring van logische testgevallen'
    norm_template = 'Maximaal {target} van de logische testgevallen is niet goedgekeurd. Meer dan {low_target} is rood.'
    template = '{name} heeft {value} niet goedgekeurde logische testgevallen van in totaal {total} gereviewde ' \
               'logische testgevallen.'
    target_value = 0
    low_target_value = 10
    quality_attribute = DOC_QUALITY

    def _nr_ltcs_ok(self):
        return self._birt.approved_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.reviewed_ltcs(self._birt_id())


class LogicalTestCasesNotAutomated(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of logical test cases that should be automated that has actually been
        automated. """

    name = 'Automatisering van logische testgevallen'
    norm_template = 'Maximaal {target} van de te automatiseren logische testgevallen is niet geautomatiseerd. ' \
        'Meer dan {low_target} is rood.'
    template = '{name} heeft {value} nog te automatiseren logische testgevallen, van in totaal {total} ' \
        'geautomatiseerde logische testgevallen.'
    target_value = 9
    low_target_value = 15
    quality_attribute = TEST_COVERAGE

    def _nr_ltcs_ok(self):
        return self._birt.nr_automated_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.nr_ltcs_to_be_automated(self._birt_id())


class ManualLogicalTestCases(BirtMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring how long ago the manual logical test cases have been tested. """

    name = 'Tijdige uitvoering van handmatige logische testgevallen'
    norm_template = 'Alle handmatige logische testgevallen zijn minder dan {target} dagen geleden uitgevoerd. ' \
        'Langer dan {low_target} dagen geleden is rood.'
    template = '{nr_manual_ltcs_too_old} van de {nr_manual_ltcs} handmatige logische testgevallen van {name} zijn ' \
        'te lang geleden (meest recente {value} dag(en), op {date}) uitgevoerd.'
    never_template = 'De {nr_manual_ltcs} handmatige logische testgevallen van {name} zijn nog niet allemaal ' \
        'uitgevoerd.'
    target_value = 21
    low_target_value = 28
    quality_attribute = TEST_COVERAGE

    def target(self):
        if self._subject.product_version_type() == 'release':
            return 0  # Release candidates should already be tested
        else:
            return self.target_value

    def low_target(self):
        return self.target() + 7

    def value(self):
        return (datetime.datetime.now() - self._date()).days

    def url(self):
        return dict(Birt=self._birt.manual_test_execution_url(self._birt_id(), self.__version()))

    def _date(self):
        return self._birt.date_of_last_manual_test(self._birt_id(), self.__version())

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ManualLogicalTestCases, self)._parameters()
        parameters['nr_manual_ltcs'] = self._birt.nr_manual_ltcs(self._birt_id(), self.__version())
        parameters['nr_manual_ltcs_too_old'] = self._birt.nr_manual_ltcs_too_old(self._birt_id(), self.__version(),
                                                                                 self.target())
        return parameters

    def _get_template(self):
        # pylint: disable=protected-access
        return self.never_template if self._date() == datetime.datetime.min \
            else super(ManualLogicalTestCases, self)._get_template()

    def __version(self):
        """ Return the version number for the product this metric is reporting on. """
        return self._subject.product_version() or 'trunk'


class NumberOfManualLogicalTestCases(LogicalTestCaseMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of manual logical test cases. """

    name = 'Aantal handmatige logische testgevallen'
    norm_template = 'Maximaal {target} van de logische testgevallen is handmatig. Meer dan {low_target} is rood.'
    template = '{value} van de {total} logische testgevallen zijn handmatig.'
    target_value = 10
    low_target_value = 50
    quality_attribute = TEST_QUALITY

    def _nr_ltcs_ok(self):
        return self._nr_ltcs() - self._birt.nr_manual_ltcs(self._birt_id())

    def _nr_ltcs(self):
        return self._birt.nr_ltcs(self._birt_id())


class DurationOfManualLogicalTestCases(JiraMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring how long it takes to execute the manual logical test cases. """

    name = 'Uitvoeringstijd handmatige logische testgevallen'
    norm_template = 'De uitvoering van de handmatige logische testgevallen kost ' \
        'maximaal {target} minuten. Meer dan {low_target} is rood.'
    template = 'De uitvoering van {measured} van de {total} handmatige logische testgevallen kost {value} minuten.'
    target_value = 120
    low_target_value = 240
    quality_attribute = TEST_QUALITY

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(DurationOfManualLogicalTestCases, cls).can_be_measured(subject, project) and \
            jira.has_manual_test_cases_query()

    def value(self):
        return self._jira.manual_test_cases_time()

    def url(self):
        return {'Jira': self._jira.manual_test_cases_url()}

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(DurationOfManualLogicalTestCases, self)._parameters()
        parameters['total'] = total = self._jira.nr_manual_test_cases()
        parameters['measured'] = total - self._jira.nr_manual_test_cases_not_measured()
        return parameters


class ManualLogicalTestCasesWithoutDuration(JiraMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring how many of the manual test cases have not been measured for duration. """

    name = 'Uitvoeringstijd handmatige logische testgevallen niet ingevuld'
    norm_template = 'Van alle handmatige logische testgevallen is de uitvoeringstijd ingevuld.'
    template = 'Van {value} van de {total} handmatige logische testgevallen is de uitvoeringstijd niet ingevuld.'
    target_value = 0
    low_target_value = 5
    quality_attribute = TEST_QUALITY

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(ManualLogicalTestCasesWithoutDuration, cls).can_be_measured(subject, project) and \
            jira.has_manual_test_cases_query()

    def value(self):
        return self._jira.nr_manual_test_cases_not_measured()

    def url(self):
        return {'Jira': self._jira.manual_test_cases_url()}

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ManualLogicalTestCasesWithoutDuration, self)._parameters()
        parameters['total'] = self._jira.nr_manual_test_cases()
        return parameters
