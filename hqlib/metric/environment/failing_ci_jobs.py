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

from typing import Dict

from hqlib import metric_source
from hqlib.domain import LowerIsBetterMetric
from hqlib.typing import MetricParameters


class FailingCIJobs(LowerIsBetterMetric):
    """ Metric for measuring the number of continuous integration jobs that fail. """

    name = 'Hoeveelheid falende CI-jobs'
    unit = 'CI-jobs'
    norm_template = 'Maximaal {target} van de actieve {unit} ' \
        'faalt. Meer dan {low_target} {unit} is rood. Een CI-job faalt als de ' \
        'laatste bouwpoging niet is geslaagd en er de afgelopen 24 uur geen ' \
        'geslaagde bouwpogingen zijn geweest. Inactieve jobs worden genegeerd.'
    template = '{value} van de {number_of_jobs} actieve {unit} faalt.'
    url_label_text = 'Falende jobs'
    target_value = 0
    low_target_value = 2
    metric_source_class = metric_source.Jenkins

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['number_of_jobs'] = str(self._metric_source.number_of_active_jobs())
        return parameters

    def value(self):
        url = self._metric_source.failing_jobs_url()
        return -1 if url is None else len(url)

    def url(self) -> Dict[str, str]:
        url = self._metric_source.failing_jobs_url()
        return dict() if url is None else url
