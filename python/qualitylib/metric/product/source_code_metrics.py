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

from ..metric_source_mixin import SonarDashboardMetricMixin, SonarViolationsMetricMixin
from ..quality_attributes import CODE_QUALITY
from ...domain import LowerPercentageIsBetterMetric


class CommentedLOC(SonarDashboardMetricMixin, LowerPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the percentage of lines of code that are commented out. """

    name = 'Uitgecommentarieerde broncode'
    norm_template = 'Maximaal {target}% van de regels code is uitgecommentarieerd. Meer dan {low_target}% is rood.'
    template = '{name} heeft {value}% ({numerator} van {denominator}) uitgecommentarieerde regels code.'
    target_value = 1
    low_target_value = 5
    quality_attribute = CODE_QUALITY

    def _numerator(self):
        return self._sonar.commented_loc(self._sonar_id())

    def _denominator(self):
        return self._sonar.ncloc(self._sonar_id())


class MethodQualityMetric(SonarViolationsMetricMixin, LowerPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Base class for metrics that measure what percentage of methods doesn't violate a certain criterium. """

    norm_template = 'Maximaal {target}% van de methoden heeft {attribute}. Meer dan {low_target}% is rood.'
    template = '{value:.0f}% van de methoden ({numerator} van {denominator}) van {name} heeft {attribute}.'
    attribute = 'Subclass responsibility'
    target_value = 0
    low_target_value = 5
    quality_attribute = CODE_QUALITY

    @classmethod
    def norm_template_default_values(cls):
        values = super(MethodQualityMetric, cls).norm_template_default_values()
        values['attribute'] = cls.attribute
        return values

    def _numerator(self):
        raise NotImplementedError  # pragma: no cover

    def _denominator(self):
        return self._sonar.methods(self._sonar_id())

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(MethodQualityMetric, self)._parameters()
        parameters['attribute'] = self.attribute
        return parameters


class CyclomaticComplexity(MethodQualityMetric):
    # pylint: disable=too-many-public-methods, too-many-ancestors
    """ Return the percentage of method whose cyclomatic complexity is too high. """

    name = 'Cyclomatische complexiteit'
    attribute = 'een cyclomatische complexiteit van 10 of hoger'

    def _numerator(self):
        return self._sonar.complex_methods(self._sonar_id())


class LongMethods(MethodQualityMetric):
    # pylint: disable=too-many-public-methods, too-many-ancestors
    """ Metric for measuring the percentage of methods that is too long. """

    name = 'Lange methoden'
    attribute = 'een lengte van meer dan 20 NCSS (Non-Comment Source Statements)'

    def _numerator(self):
        return self._sonar.long_methods(self._sonar_id())


class ManyParameters(MethodQualityMetric):
    # pylint: disable=too-many-public-methods, too-many-ancestors
    """ Metric for measuring the percentage of methods that have too many parameters. """

    name = 'Methoden met te veel parameters'
    attribute = 'meer dan 5 parameters'

    def _numerator(self):
        return self._sonar.many_parameters_methods(self._sonar_id())
