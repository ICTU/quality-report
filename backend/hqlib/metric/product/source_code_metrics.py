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


from hqlib.typing import MetricParameters
from ..metric_source_mixin import SonarDashboardMetric, SonarViolationsMetric
from ...domain import LowerPercentageIsBetterMetric


class CommentedLOC(SonarDashboardMetric, LowerPercentageIsBetterMetric):
    """ Metric for measuring the percentage of lines of code that are commented out. """

    name = 'Hoeveelheid uitgecommentarieerde broncode'
    norm_template = 'Maximaal {target}{unit} van de regels code is uitgecommentarieerd. ' \
                    'Meer dan {low_target}{unit} is rood.'
    template = '{name} heeft {value}{unit} ({numerator} van {denominator}) uitgecommentarieerde regels code.'
    target_value = 1
    low_target_value = 5

    def _numerator(self):
        return self._metric_source.commented_loc(self._sonar_id()) if self._metric_source else -1

    def _denominator(self):
        return self._metric_source.ncloc(self._sonar_id()) if self._metric_source else -1


class MethodQualityMetric(SonarViolationsMetric, LowerPercentageIsBetterMetric):
    """ Base class for metrics that measure what percentage of methods doesn't violate a certain criterium. """

    norm_template = 'Maximaal {target}{unit} van de methoden heeft {attribute}. Meer dan {low_target}{unit} is rood.'
    template = '{value:.0f}{unit} van de methoden ({numerator} van {denominator}) van {name} heeft {attribute}.'
    attribute = 'Subclass responsibility'
    target_value = 0
    low_target_value = 5

    @classmethod
    def norm_template_default_values(cls) -> MetricParameters:
        values = super(MethodQualityMetric, cls).norm_template_default_values()
        values['attribute'] = cls.attribute
        return values

    def _numerator(self):
        raise NotImplementedError

    def _denominator(self):
        return self._metric_source.methods(self._sonar_id()) if self._metric_source else -1

    def _parameters(self) -> MetricParameters:
        # pylint: disable=protected-access
        parameters = super()._parameters()
        parameters['attribute'] = self.attribute
        return parameters


class CyclomaticComplexity(MethodQualityMetric):
    # pylint: disable=too-many-ancestors
    """ Return the percentage of method whose cyclomatic complexity is too high. """

    name = 'Cyclomatische complexiteit'
    attribute = 'een cyclomatische complexiteit van 10 of hoger'

    def _numerator(self):
        return self._metric_source.complex_methods(self._sonar_id()) if self._metric_source else -1


class LongMethods(MethodQualityMetric):
    # pylint: disable=too-many-ancestors
    """ Metric for measuring the percentage of methods that is too long. """

    name = 'Lengte van methoden'
    attribute = 'een lengte van meer dan 20 NCSS (Non-Comment Source Statements)'

    def _numerator(self):
        return self._metric_source.long_methods(self._sonar_id()) if self._metric_source else -1


class ManyParameters(MethodQualityMetric):
    # pylint: disable=too-many-ancestors
    """ Metric for measuring the percentage of methods that have too many parameters. """

    name = 'Hoeveelheid methoden met te veel parameters'
    attribute = 'meer dan 5 parameters'

    def _numerator(self):
        return self._metric_source.many_parameters_methods(self._sonar_id()) if self._metric_source else -1
