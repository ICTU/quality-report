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

import json
from typing import Dict
from hqlib import metric_source, utils
from hqlib.domain import LowerIsBetterMetric, ExtraInfo
from hqlib.typing import MetricParameters


class CIJobs(LowerIsBetterMetric):
    """ Base class for FailingCIJobs and UnusedCIJobs. """

    metric_source_class = metric_source.CIServer
    _qualifier = ''

    def _parameters(self) -> MetricParameters:
        parameters = super()._parameters()
        parameters['number_of_jobs'] = str(self._metric_source.number_of_active_jobs()) if self._metric_source else '?'
        return parameters

    def url(self) -> Dict[str, str]:
        """ Returns formal empty parameter for format_text_with_links."""
        return dict()

    def _jobs_url(self) -> list((str, str, str)):
        raise NotImplementedError

    def format_text_with_links(self, text: str, url_dict: Dict[str, str] = None, url_label: str = None) -> str:
        """ Format a text paragraph with additional url. """
        return json.dumps(utils.html_escape(text).replace('\n', ' '))[1:-1]

    def extra_info(self) -> ExtraInfo:
        """ Returns a list with unmerged branches as an extra info object. """
        extra_info = None
        if self._metric_source:
            url_list = self._jobs_url()
            if url_list:
                extra_info = ExtraInfo(link="Job naam", comment="Aantal dagen {qual}".format(qual=self._qualifier))
                extra_info.title = self.url_label_text
                for name, url, days in url_list:
                    extra_info += {"href": url, "text": name}, days

        return extra_info if extra_info is not None and extra_info.data else None
