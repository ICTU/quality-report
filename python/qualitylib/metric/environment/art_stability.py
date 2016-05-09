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

from qualitylib.domain import Metric
from qualitylib.metric.metric_source_mixin import JenkinsMetricMixin
from qualitylib.metric.quality_attributes import TEST_QUALITY


class ARTStability(JenkinsMetricMixin, Metric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the stability of an ART. An ART is considered to
        be unstable if it hasn't succeeded for multiple days. """

    name = 'Stabiliteit van automatische regressietest'
    norm_template = 'Alle regressietesten en integratietesten hebben de laatste {target} dagen minimaal eenmaal ' \
        'succesvol gedraaid. Rood als er testen meer dan {low_target} dagen niet succesvol hebben gedraaid.'
    above_target_template = 'Alle ARTs hebben de afgelopen {target} dagen succesvol gedraaid in de "{street}"-straat.'
    below_target_template = '{value} ARTs hebben de afgelopen {target} dagen niet succesvol gedraaid in de ' \
        '"{street}"-straat.'
    target_value = 3
    low_target_value = 7
    quality_attribute = TEST_QUALITY

    def value(self, days=0):
        """ Return the number of failing jobs in the ART-street in the last days. """
        return len(self._jenkins.unstable_arts_url(self.__street_regexp(), days=days or self.target()))

    def numerical_value(self):
        """ Return the number of failing jobs. """
        return self.value(days=self.target())

    def _is_below_target(self):
        return self.value(days=self.target()) > 0

    def _needs_immediate_action(self):
        return self.value(days=self.low_target()) > 0

    def _is_perfect(self):
        return self.value(days=1) == 0

    def _get_template(self):
        return self.below_target_template if self.value() > 0 else self.above_target_template

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ARTStability, self)._parameters()
        parameters['street'] = self.__street_name()
        return parameters

    def url(self):
        """ Return the urls for the failing jobs. """
        urls = dict()
        urls.update(self._jenkins.unstable_arts_url(self.__street_regexp(), days=self.target()))
        street_url = self._subject.url()
        if street_url:
            urls['"{street}"-straat'.format(street=self.__street_name())] = street_url
        return urls

    def __street_name(self):
        """ Return the name of the street. """
        return self._subject.name()

    def __street_regexp(self):
        """ Return the regular expression for the ARTs in the street. """
        return self._subject.regexp()
