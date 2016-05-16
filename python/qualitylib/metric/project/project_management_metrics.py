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

from .. import LowerIsBetterMetric
from ..metric_source_mixin import TrelloActionsBoardMetricMixin
from ..quality_attributes import PROJECT_MANAGEMENT
from ... import metric_source
from ...metric_source import TrelloUnreachableException


class RiskLog(LowerIsBetterMetric):
    """ Metric for measuring the number of days since the risk log was last updated. """

    name = 'Actualiteit risico log'
    norm_template = 'Het risicolog wordt minimaal een keer per {target} dagen bijgewerkt. ' \
        'Meer dan {low_target} dagen niet bijgewerkt is rood.'
    template = 'Het risicolog is {value} dagen geleden (op {date}) voor het laatst bijgewerkt.'
    target_value = 14
    low_target_value = 28
    quality_attribute = PROJECT_MANAGEMENT
    metric_source_classes = (metric_source.TrelloRiskBoard,)

    def __init__(self, *args, **kwargs):
        super(RiskLog, self).__init__(*args, **kwargs)
        self.__trello_risklog_board = self._project.metric_source(metric_source.TrelloRiskBoard)

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
    """ Metric for measuring the number of days since the actions were last updated. """

    name = 'Actualiteit actielijst'
    norm_template = 'De actie- en besluitenlijst wordt minimaal een keer per {target} dagen bijgewerkt. ' \
        'Meer dan {low_target} dagen niet bijgewerkt is rood.'
    template = 'De actie- en besluitenlijst is {value} dagen geleden (op {date}) voor het laatst bijgewerkt.'
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
    """ Metric for measuring the age of individual actions. """

    name = 'Tijdigheid acties'
    norm_template = 'Geen van de acties en besluiten in de actie- en besluitenlijst is te laat of te lang ' \
        '(14 dagen) niet bijgewerkt. Meer dan {low_target} acties te laat of te lang niet bijgewerkt is rood.'
    template = '{value} acties uit de actie- en besluitenlijst zijn te laat of te lang (14 dagen) niet bijgewerkt.'
    url_label_text = 'Niet bijgewerkte of te late acties'
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
