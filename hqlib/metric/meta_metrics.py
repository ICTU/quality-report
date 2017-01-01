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

from ..domain import HigherPercentageIsBetterMetric, LowerPercentageIsBetterMetric


class MetaMetricMixin(object):  # pylint: disable=too-few-public-methods
    """ Mixin class for meta metrics. Assumes that meta metrics are percentage metrics and that the subclass
        specifies the metric statuses (colors) that the meta metric is measuring. """
    metric_statuses = []  # Subclass responsibility

    def _numerator(self):
        """ Return the numerator (the number above the divider) for the meta metric. """
        return len([metric for metric in self._subject if metric.status() in self.metric_statuses])

    def _denominator(self):
        """ Return the denominator (the number below the divider) for the meta metric. """
        return len(self._subject)


class GreenMetaMetric(MetaMetricMixin, HigherPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores green. """

    metric_statuses = ('green', 'perfect')
    norm_template = 'Minimaal {target}{unit} van de metrieken scoort groen (op of boven de norm). ' \
                    'Minder dan {low_target}{unit} is rood.'
    template = '{value}{unit} van de metrieken ({numerator} van de {denominator}) scoort boven de norm.'
    target_value = 90
    low_target_value = 80


class RedMetaMetric(MetaMetricMixin, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores red. """

    metric_statuses = ('red',)
    norm_template = 'Maximaal {target}{unit} van de metrieken scoort rood (direct actie vereist). ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = '{value}{unit} van de metrieken ({numerator} van de {denominator}) scoort rood.'
    target_value = 2
    low_target_value = 5


class YellowMetaMetric(MetaMetricMixin, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores yellow. """

    metric_statuses = ('yellow',)
    norm_template = 'Maximaal {target}{unit} van de metrieken scoort geel ' \
                    '(onder de norm maar niet direct actie vereist). Meer dan {low_target}{unit} is rood.'
    template = '{value}{unit} van de metrieken ({numerator} van de {denominator}) scoort geel.'
    target_value = 5
    low_target_value = 10


class GreyMetaMetric(MetaMetricMixin, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores grey. """

    metric_statuses = ('grey',)
    norm_template = 'Maximaal {target}{unit} van de metrieken scoort grijs (geaccepteerde technische schuld). ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = '{value}% van de metrieken ({numerator} van de {denominator}) scoort grijs.'
    target_value = 2
    low_target_value = 5


class MissingMetaMetric(MetaMetricMixin, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that can't be measured. """

    metric_statuses = ('missing', 'missing_source')
    norm_template = 'Maximaal {target}{unit} van de metrieken kan niet gemeten worden. ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = '{value}{unit} van de metrieken ({numerator} van de {denominator}) kan niet gemeten worden.'
    target_value = 0
    low_target_value = 5
