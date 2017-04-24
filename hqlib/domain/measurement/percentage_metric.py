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

import functools
from typing import Tuple

from . import directed_metric
from . import metric
from ... import utils
from hqlib.typing import MetricParameters, MetricValue


class PercentageMetric(metric.Metric):
    """ Base class for metrics that are calculated as the percentage of a numerator and a denominator. """

    unit = '%'
    zero_divided_by_zero_is_zero = False

    @functools.lru_cache(maxsize=1024)
    def value(self):
        """ Return the actual value of the metric as a percentage calculated from the numerator and denominator
            of the metric. """
        numerator, denominator = self._numerator(), self._denominator()
        if -1 in (numerator, denominator) or None in (numerator, denominator):
            return -1
        else:
            return utils.percentage(numerator, denominator, self.zero_divided_by_zero_is_zero)

    def _is_value_better_than(self, target: MetricValue) -> bool:
        """ Return whether the actual value of the metric is better than the specified target value. """
        return super()._is_value_better_than(target)

    def _parameters(self) -> MetricParameters:
        """ Add numerator and denominator to the parameters. """
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters.update(dict(numerator=str(self._numerator()), denominator=str(self._denominator())))
        return parameters

    def _numerator(self) -> int:
        """ Return the numerator (the number above the divider) for the metric. """
        raise NotImplementedError  # pragma: no cover

    def _denominator(self) -> int:
        """ Return the denominator (the number below the divider) for the metric. """
        raise NotImplementedError  # pragma: no cover

    def y_axis_range(self) -> Tuple[int, int]:
        """ Return the y-axis range. This is always 0-100, since this class represents a metric measured as
            percentage. """
        return 0, 100


class LowerPercentageIsBetterMetric(PercentageMetric, directed_metric.LowerIsBetterMetric):
    """ Metric measured as a percentage with lower values being better. """

    zero_divided_by_zero_is_zero = True

    @functools.lru_cache(maxsize=1024)
    def _numerator(self) -> int:
        raise NotImplementedError  # pragma: no cover

    def _denominator(self) -> int:
        raise NotImplementedError  # pragma: no cover


class HigherPercentageIsBetterMetric(PercentageMetric, directed_metric.HigherIsBetterMetric):
    """ Metric measured as a percentage with higher values being better. """

    perfect_value = 100

    @functools.lru_cache(maxsize=1024)
    def _numerator(self) -> int:
        raise NotImplementedError  # pragma: no cover

    def _denominator(self) -> int:
        raise NotImplementedError  # pragma: no cover
