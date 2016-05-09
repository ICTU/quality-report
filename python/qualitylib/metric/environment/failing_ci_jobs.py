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

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import JenkinsMetricMixin
from qualitylib.metric.quality_attributes import ENVIRONMENT_QUALITY


class FailingCIJobs(JenkinsMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of continuous integration jobs that fail. """

    name = 'Falende CI-jobs'
    norm_template = 'Maximaal {target} van de actieve CI-jobs ' \
        'faalt. Meer dan {low_target} is rood. Een CI-job faalt als de ' \
        'laatste bouwpoging niet is geslaagd en er de afgelopen 24 uur geen ' \
        'geslaagde bouwpogingen zijn geweest. Inactieve jobs worden genegeerd.'
    template = '{value} van de {number_of_jobs} actieve CI-jobs faalt.'
    url_label_text = 'Falende jobs'
    target_value = 0
    low_target_value = 2
    quality_attribute = ENVIRONMENT_QUALITY

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingCIJobs, self)._parameters()
        parameters['number_of_jobs'] = self._jenkins.number_of_active_jobs()
        return parameters

    def value(self):
        return len(self._jenkins.failing_jobs_url())

    def url(self):
        return self._jenkins.failing_jobs_url()
