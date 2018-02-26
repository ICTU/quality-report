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

from . import CIJobs


class UnusedCIJobs(CIJobs):
    """ Metric for measuring the number of continuous integration jobs that are not used. """

    name = 'Hoeveelheid ongebruikte CI-jobs'
    unit = 'CI-jobs'
    norm_template = 'Maximaal {target} van de actieve {unit} is ongebruikt. Meer dan {low_target} {unit} is rood. ' \
        'Een CI-job is ongebruikt als er de afgelopen 6 maanden geen bouwpogingen zijn geweest. Inactieve ' \
        '{unit} worden genegeerd.'
    template = '{value} van de {number_of_jobs} actieve {unit} is ongebruikt.'
    url_label_text = 'Ongebruikte jobs'
    target_value = 0
    low_target_value = 2
    extra_info_headers = {"link": "Job naam", "comment": "Aantal dagen ongebruikt__detail-column-number"}

    def value(self):
        """ Return the number of unused jobs. """
        return self._metric_source.number_of_unused_jobs() if self._metric_source else -1

    def extra_info_urls(self) -> list((str, str, str)):
        return self._metric_source.unused_jobs_url()
