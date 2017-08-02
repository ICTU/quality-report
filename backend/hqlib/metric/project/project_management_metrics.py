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


import datetime
from typing import Dict

from hqlib import metric_source
from hqlib.domain import LowerIsBetterMetric
from hqlib.typing import MetricValue


class ActivityMetric(LowerIsBetterMetric):
    """ Metrics for tracking actuality using Trello. """

    unit = 'dagen'

    def value(self) -> MetricValue:
        return -1 if self._missing() else (datetime.datetime.now() - self._metric_source.datetime()).days

    def _missing(self) -> bool:
        return self._metric_source.datetime() in (None, datetime.datetime.min)


class RiskLog(ActivityMetric):
    """ Metric for measuring the number of days since the risk log was last updated. """

    name = 'Actualiteit van de risico log'
    norm_template = 'Het risicolog wordt minimaal een keer per {target} {unit} bijgewerkt. ' \
        'Meer dan {low_target} {unit} niet bijgewerkt is rood.'
    template = 'Het risicolog is {value} {unit} geleden voor het laatst bijgewerkt.'
    target_value = 14
    low_target_value = 28
    metric_source_class = metric_source.TrelloRiskBoard


class ActionActivity(ActivityMetric):
    """ Metric for measuring the number of days since the actions were last updated. """

    name = 'Actualiteit van de actielijst'
    norm_template = 'De actie- en besluitenlijst wordt minimaal een keer per {target} {unit} bijgewerkt. ' \
        'Meer dan {low_target} {unit} niet bijgewerkt is rood.'
    template = 'De actie- en besluitenlijst is {value} {unit} geleden voor het laatst bijgewerkt.'
    target_value = 7
    low_target_value = 14
    metric_source_class = metric_source.TrelloActionsBoard


class OverDueActions(LowerIsBetterMetric):
    """ Metric for measuring the number of over due actions. """

    name = 'Tijdigheid van de acties'
    unit = 'acties'
    norm_template = 'Geen van de acties en besluiten in de actie- en besluitenlijst is te laat. ' \
                    'Meer dan {low_target} {unit} te laat is rood.'
    template = '{value} {unit} uit de actie- en besluitenlijst zijn te laat.'
    url_label_text = 'Te late acties'
    target_value = 0
    low_target_value = 3
    metric_source_class = metric_source.TrelloActionsBoard

    def value(self) -> MetricValue:
        nr_cards = self._metric_source.nr_of_over_due_cards()
        return -1 if nr_cards is None else nr_cards

    def url(self) -> Dict[str, str]:
        return self._metric_source.over_due_cards_url() or {}


class StaleActions(LowerIsBetterMetric):
    """ Metric for measuring the staleness of actions . """

    name = 'Actualiteit van de acties'
    unit = 'acties'
    norm_template = 'Geen van de acties en besluiten in de actie- en besluitenlijst is te lang ' \
        '(14 dagen) niet bijgewerkt. Meer dan {low_target} {unit} te lang niet bijgewerkt is rood.'
    template = '{value} {unit} uit de actie- en besluitenlijst zijn te lang (14 dagen) niet bijgewerkt.'
    url_label_text = 'Niet bijgewerkte acties'
    target_value = 0
    low_target_value = 3
    metric_source_class = metric_source.TrelloActionsBoard

    def value(self) -> MetricValue:
        nr_cards = self._metric_source.nr_of_inactive_cards()
        return -1 if nr_cards is None else nr_cards

    def url(self) -> Dict[str, str]:
        return self._metric_source.inactive_cards_url() or {}

