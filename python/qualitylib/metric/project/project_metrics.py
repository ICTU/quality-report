'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import utils, metric_source
from qualitylib.metric import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import \
    TrelloActionsBoardMetricMixin, JiraMetricMixin
from qualitylib.metric_source import TrelloUnreachableException
from qualitylib.metric.quality_attributes import PROJECT_MANAGEMENT, PROGRESS, \
    TEST_QUALITY, SECURITY
import datetime


class RiskLog(LowerIsBetterMetric):
    ''' Metric for measuring the number of days since the risk log was last
        updated. '''

    name = 'Actualiteit risico log'
    norm_template = 'Het risicolog wordt minimaal een keer per %(target)d ' \
        'dagen bijgewerkt. Meer dan %(low_target)d dagen niet bijgewerkt is ' \
        'rood.'
    template = 'Het risicolog is %(value)d dagen geleden (op %(date)s) voor ' \
        'het laatst bijgewerkt.'
    target_value = 14
    low_target_value = 28
    quality_attribute = PROJECT_MANAGEMENT

    def __init__(self, *args, **kwargs):
        super(RiskLog, self).__init__(*args, **kwargs)
        self.__trello_risklog_board = \
            self._project.metric_source(metric_source.TrelloRiskBoard)

    @classmethod
    def can_be_measured(cls, subject, project):
        return super(RiskLog, cls).can_be_measured(subject, project) and \
            project.metric_source(metric_source.TrelloRiskBoard)

    def value(self):
        return (datetime.datetime.now() - self._date()).days

    def _date(self):
        try:
            return self.__trello_risklog_board.date_of_last_update()
        except TrelloUnreachableException:
            return datetime.datetime.min

    def url(self):
        try:
            url = self.__trello_risklog_board.url()
        except TrelloUnreachableException:
            url = 'http://trello.com'
        return dict(Trello=url)


class ActionActivity(TrelloActionsBoardMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the number of days since the actions were last
        updated. '''

    name = 'Actualiteit actielijst'
    norm_template = 'De actie- en besluitenlijst wordt minimaal een keer ' \
        'per %(target)d dagen bijgewerkt. Meer dan %(low_target)d dagen ' \
        'niet bijgewerkt is rood.'
    template = 'De actie- en besluitenlijst is %(value)d dagen geleden ' \
        '(op %(date)s) voor het laatst bijgewerkt.'
    target_value = 7
    low_target_value = 14
    quality_attribute = PROJECT_MANAGEMENT

    def value(self):
        return (datetime.datetime.now() - self._date()).days

    def _date(self):
        try:
            return self._trello_actions_board.date_of_last_update()
        except TrelloUnreachableException:
            return datetime.datetime.min

    def url(self):
        try:
            url = self._trello_actions_board.url()
        except TrelloUnreachableException:
            url = 'http://trello.com'
        return dict(Trello=url)


class ActionAge(TrelloActionsBoardMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the age of individual actions. '''

    name = 'Tijdigheid acties'
    norm_template = 'Geen van de acties en besluiten in de actie- en ' \
        'besluitenlijst is te laat of te lang (14 dagen) niet bijgewerkt. ' \
        'Meer dan %(low_target)d acties te laat of te lang niet bijgewerkt ' \
        'is rood.'
    template = '%(value)d acties uit de actie- en besluitenlijst zijn te ' \
        'laat of te lang (14 dagen) niet bijgewerkt.'
    target_value = 0
    low_target_value = 3
    quality_attribute = PROJECT_MANAGEMENT

    def value(self):
        try:
            return self._trello_actions_board.nr_of_over_due_or_inactive_cards()
        except TrelloUnreachableException:
            return -1

    def url(self):
        try:
            return self._trello_actions_board.over_due_or_inactive_cards_url()
        except TrelloUnreachableException:
            return dict(Trello='http://trello.com')

    def url_label(self):
        return 'Niet bijgewerkte of te late acties'


class OpenBugs(JiraMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the number of open bug reports. '''

    name = 'Open bugreports'
    norm_template = 'Het aantal open bug reports is minder dan %(target)d. ' \
       'Meer dan %(low_target)d is rood.'
    template = 'Het aantal open bug reports is %(value)d.'
    target_value = 50
    low_target_value = 100
    quality_attribute = PROGRESS

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(OpenBugs, cls).can_be_measured(subject, project) and \
            jira.has_open_bugs_query()

    def value(self):
        return self._jira.nr_open_bugs()

    def url(self):
        return {'Jira': self._jira.nr_open_bugs_url()}


class OpenSecurityBugs(JiraMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the number of open security bugs. '''

    name = 'Open beveiligingsbugreports'
    norm_template = 'Het aantal beveiliging bug reports dat meer dan een ' \
        'sprint open staat is minder dan %(target)d. Meer dan %(low_target)d ' \
        'is rood.'
    template = 'Het aantal beveiliging bug reports dat meer dan een sprint ' \
        'open staat is %(value)d.'
    target_value = 0
    low_target_value = 3
    quality_attribute = SECURITY

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(OpenSecurityBugs, cls).can_be_measured(subject, 
                                                            project) and \
            jira.has_open_security_bugs_query()

    def value(self):
        return self._jira.nr_open_security_bugs()

    def url(self):
        return {'Jira': self._jira.nr_open_security_bugs_url()}


class BlockingTestIssues(JiraMetricMixin, LowerIsBetterMetric):
    ''' Metric for measuring the number of blocking test issues opened the
        previous month. '''

    name = 'Aantal blokkerende testbevindingen'
    norm_template = 'Het aantal geopende blokkerende testbevindingen is ' \
        'maximaal %(target)d. Meer dan %(low_target)d is rood.'
    template = 'Het aantal geopende blokkerende testbevindingen in de vorige ' \
        'maand (%(month)s) was %(value)d.'
    target_value = 0
    low_target_value = 1
    quality_attribute = TEST_QUALITY

    @classmethod
    def can_be_measured(cls, subject, project):
        jira = project.metric_source(metric_source.Jira)
        return super(BlockingTestIssues, cls).can_be_measured(subject, 
                                                              project) and \
            jira.has_blocking_test_issues_query()

    def value(self):
        return self._jira.nr_blocking_test_issues()

    def url(self):
        return {'Jira': self._jira.nr_blocking_test_issues_url()}

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(BlockingTestIssues, self)._parameters()
        parameters['month'] = utils.format_month(utils.month_ago())
        return parameters
