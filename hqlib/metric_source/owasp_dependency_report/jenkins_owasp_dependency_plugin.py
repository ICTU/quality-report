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

import logging
from typing import List

from .. import url_opener
from ..abstract import owasp_dependency_report
from ..jenkins import Jenkins
from hqlib.typing import DateTime


class JenkinsOWASPDependencyReport(owasp_dependency_report.OWASPDependencyReport, Jenkins):
    """ Class representing OWASP dependency reports in Jenkins jobs. """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__report_url = self._last_successful_build_url + 'dependency-check-jenkins-pluginResult/'
        self.__report_api_url = self.__report_url + self.api_postfix

    def _nr_warnings(self, job_name: str, priority: str) -> int:
        """ Return the number of warnings of the specified type in the job. """
        job_name = self.resolve_job_name(job_name)
        url = self.__report_api_url.format(job=job_name)
        try:
            report_dict = self._api(url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't open %s to read warning count %s: %s", url, priority, reason)
            return -1
        return int(report_dict['numberOf{0}PriorityWarnings'.format(priority.capitalize())])

    def metric_source_urls(self, *job_names: str) -> List[str]:
        """ Return the url of the job. """
        return [self.__report_url.format(job=self.resolve_job_name(job_name)) for job_name in job_names]

    def _report_datetime(self, job_name: str) -> DateTime:
        """ Return the date and time of one report. """
        job_name = self.resolve_job_name(job_name)
        return self.job_datetime(dict(name=job_name), self._last_stable_build_url)
