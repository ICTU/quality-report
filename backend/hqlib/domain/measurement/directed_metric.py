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

from hqlib.typing import MetricValue
from . import metric


class LowerIsBetterMetric(metric.Metric):
    """ Metric for which a lower value means the metric is scoring better. """

    perfect_value = 0
    norm_template = "Maximaal {target} {unit}. Meer dan {low_target} {unit} is rood."

    @functools.lru_cache(maxsize=1024)
    def value(self) -> MetricValue:
        return super().value()  # pragma: no cover

    def _is_value_better_than(self, target: MetricValue) -> bool:
        return self.perfect_value <= self.value() <= target


class HigherIsBetterMetric(metric.Metric):
    """ Metric for which a higher value means the metric is scoring better. """

    norm_template = "Minimaal {target} {unit}. Minder dan {low_target} {unit} is rood."

    @functools.lru_cache(maxsize=1024)
    def value(self) -> MetricValue:
        return super().value()  # pragma: no cover

    def _is_value_better_than(self, target: MetricValue) -> bool:
        return self.value() >= target
