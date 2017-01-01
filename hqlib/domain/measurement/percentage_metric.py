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

from . import directed_metric
from ... import utils


class PercentageMixin(object):
    """ Mixin class for metrics that are calculated as the percentage of a numerator and a denominator. """

    unit = '%'
    zero_divided_by_zero_is_zero = 'Subclass responsibility'

    @utils.memoized
    def value(self):
        """ Return the actual value of the metric as a percentage calculated from the numerator and denominator
            of the metric. """
        numerator, denominator = self._numerator(), self._denominator()
        if -1 in (numerator, denominator) or None in (numerator, denominator):
            return -1
        else:
            return utils.percentage(numerator, denominator, self.zero_divided_by_zero_is_zero)

    def _parameters(self):
        """ Add numerator and denominator to the parameters. """
        # pylint: disable=protected-access
        parameters = super(PercentageMixin, self)._parameters()
        parameters.update(dict(numerator=self._numerator(), denominator=self._denominator()))
        return parameters

    def _numerator(self):
        """ Return the numerator (the number above the divider) for the metric. """
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        """ Return the denominator (the number below the divider) for the metric. """
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def y_axis_range():
        """ Return the y-axis range. This is always 0-100, since this class represents a metric measured as
            percentage. """
        return 0, 100


class LowerPercentageIsBetterMetric(PercentageMixin, directed_metric.LowerIsBetterMetric):
    """ Metric measured as a percentage with lower values being better. """

    zero_divided_by_zero_is_zero = True

    def _numerator(self):
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        raise NotImplementedError  # pragma: no cover


class HigherPercentageIsBetterMetric(PercentageMixin, directed_metric.HigherIsBetterMetric):
    """ Metric measured as a percentage with higher values being better. """

    perfect_value = 100
    zero_divided_by_zero_is_zero = False

    def _numerator(self):
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        raise NotImplementedError  # pragma: no cover
