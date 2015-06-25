'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import absolute_import


# CI: Continuous integration metrics.

from .metric_source_mixin import JenkinsMetricMixin
from .quality_attributes import \
    ENVIRONMENT_QUALITY, \
    TEST_QUALITY
from ..domain import \
    Metric, \
    LowerIsBetterMetric, \
    HigherPercentageIsBetterMetric


class ARTStability(JenkinsMetricMixin, Metric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the stability of an ART. An ART is considered to
        be unstable if it hasn't succeeded for multiple days. '''

    name = 'Stabiliteit van automatische regressietest'
    norm_template = 'Alle regressietesten en integratietesten hebben de ' \
        'laatste {target} dagen minimaal eenmaal succesvol gedraaid. Rood ' \
        'als er testen meer dan {low_target} dagen niet succesvol ' \
        'hebben gedraaid.'
    above_target_template = 'Alle ARTs hebben de afgelopen {target} dagen ' \
        'succesvol gedraaid in de "{street}"-straat.'
    below_target_template = '{value} ARTs hebben de ' \
        'afgelopen {target} dagen niet succesvol gedraaid in de ' \
        '"{street}"-straat.'
    target_value = 3
    low_target_value = 7
    quality_attribute = TEST_QUALITY

    def value(self, days=0):  # pylint: disable=W0221
        return len(self._jenkins.unstable_arts_url(self.__street_regexp(), 
                                                   days=days or self.target()))

    def numerical_value(self):
        return self.value(days=self.target())

    def _is_below_target(self):
        return self.value(days=self.target()) > 0

    def _needs_immediate_action(self):
        return self.value(days=self.low_target()) > 0

    def _is_perfect(self):
        return self.value(days=1) == 0

    def _get_template(self):
        return self.below_target_template if self.value() > 0 \
            else self.above_target_template

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ARTStability, self)._parameters()
        parameters['street'] = self.__street_name()
        return parameters

    def url(self):
        urls = dict()
        urls.update(self._jenkins.unstable_arts_url(self.__street_regexp(), 
                                                    days=self.target()))
        street_url = self._subject.url()
        if street_url:
            urls['"{street}"-straat'.format(street=self.__street_name())] = street_url
        return urls

    def __street_name(self):
        ''' Return the name of the street. '''
        return self._subject.name()

    def __street_regexp(self):
        ''' Return the regular expression for the ARTs in the street. '''
        return self._subject.regexp()


class FailingCIJobs(JenkinsMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that fail. '''

    name = 'Falende CI-jobs'
    norm_template = 'Maximaal {target} van de CI-jobs ' \
        'faalt. Meer dan {low_target} is rood. Een CI-job faalt als de ' \
        'laatste bouwpoging niet is geslaagd en er de afgelopen 24 uur geen ' \
        'geslaagde bouwpogingen zijn geweest.'
    template = '{value} van de {number_of_jobs} CI-jobs faalt.'
    target_value = 0
    low_target_value = 2
    quality_attribute = ENVIRONMENT_QUALITY

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingCIJobs, self)._parameters()
        parameters['number_of_jobs'] = self._jenkins.number_of_jobs()
        return parameters

    def value(self):
        return len(self._jenkins.failing_jobs_url())

    def url(self):
        return self._jenkins.failing_jobs_url()

    def url_label(self):
        return 'Falende jobs'


class UnusedCIJobs(JenkinsMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that are not used. '''

    name = 'Ongebruikte CI-jobs'
    norm_template = 'Maximaal {target} van de CI-jobs ' \
        'is ongebruikt. Meer dan {low_target} is rood. Een CI-job is ' \
        'ongebruikt als er de afgelopen 6 maanden geen bouwpogingen zijn ' \
        'geweest.'
    template = '{value} van de {number_of_jobs} CI-jobs is ongebruikt.'
    target_value = 0
    low_target_value = 2
    quality_attribute = ENVIRONMENT_QUALITY

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(UnusedCIJobs, self)._parameters()
        parameters['number_of_jobs'] = self.__number_of_jobs()
        return parameters

    def value(self):
        return len(self._jenkins.unused_jobs_url())

    def url(self):
        return self._jenkins.unused_jobs_url()

    def url_label(self):
        return 'Ongebruikte jobs'

    def __number_of_jobs(self):
        ''' Return the total number of jobs. '''
        return self._jenkins.number_of_jobs()
