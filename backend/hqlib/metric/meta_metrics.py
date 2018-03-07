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

import functools

from typing import Tuple

from hqlib.typing import MetricParameters
from ..domain import PercentageMetric, HigherPercentageIsBetterMetric, LowerPercentageIsBetterMetric


class MetaMetric(PercentageMetric):  # pylint: disable=too-few-public-methods
    """ Base class for meta metrics. Assumes that meta metrics are percentage metrics and that the subclass
        specifies the metric statuses (colors) that the meta metric is measuring. """
    metric_statuses: Tuple = tuple()  # Subclass responsibility
    status_text1 = status_text2 = status_color_text = "Subclass responsibility"
    target_prefix_text = "Maximaal"
    low_target_prefix_text = "meer"
    norm_template = '{target_prefix_text} {target}{unit} van de metrieken {status_text1} (is {status_color_text}). ' \
                    'Als {low_target_prefix_text} dan {low_target}{unit} van de metrieken {status_text2} is ' \
                    'deze metriek rood.'
    template = '{value}{unit} van de metrieken ({numerator} van de {denominator}) {status_text1}.'

    @functools.lru_cache(maxsize=1024)
    def value(self):
        return super().value()

    def _is_value_better_than(self, target):
        return super()._is_value_better_than(target)

    @functools.lru_cache(maxsize=1024)
    def _numerator(self) -> int:
        """ Return the numerator (the number above the divider) for the meta metric. """
        return len([metric for metric in self._subject if metric.status() in self.metric_statuses])

    def _denominator(self) -> int:
        """ Return the denominator (the number below the divider) for the meta metric. """
        return len(self._subject)

    def _parameters(self) -> MetricParameters:
        """ Add the status text fragments to the parameters so they can be used in the templates. """
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters["status_text1"] = self.status_text1
        parameters["status_text2"] = self.status_text2
        parameters["status_color_text"] = self.status_color_text
        parameters["target_prefix_text"] = self.target_prefix_text
        parameters["low_target_prefix_text"] = self.low_target_prefix_text
        return parameters


class GreenMetaMetric(MetaMetric, HigherPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores green. """

    metric_statuses = ('green', 'perfect')
    status_text1 = "voldoet aan de norm"
    status_text2 = "aan de norm voldoet"
    target_prefix_text = "Minimaal"
    low_target_prefix_text = "minder"
    status_color_text = "groen"
    target_value = 80
    low_target_value = 70


class RedMetaMetric(MetaMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores red. """

    metric_statuses = ('red',)
    status_text1 = "vereist direct actie"
    status_text2 = "direct actie vereist"
    status_color_text = "rood"
    target_value = 10
    low_target_value = 20


class YellowMetaMetric(MetaMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores yellow. """

    metric_statuses = ('yellow',)
    status_text1 = "voldoet net niet aan de norm"
    status_text2 = "net niet aan de norm voldoet"
    status_color_text = "geel"
    target_value = 20
    low_target_value = 30


class GreyMetaMetric(MetaMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that scores grey. """

    metric_statuses = ('grey',)
    status_text1 = "heeft geaccepteerde technische schuld"
    status_text2 = "geaccepteerde technische schuld heeft"
    status_color_text = "grijs"
    target_value = 20
    low_target_value = 30


class MissingMetaMetric(MetaMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of metrics that can't be measured. """

    metric_statuses = ('missing', 'missing_source')
    status_text1 = "kan niet gemeten worden"
    status_text2 = "niet gemeten kan worden"
    status_color_text = "wit"
    target_value = 20
    low_target_value = 30
