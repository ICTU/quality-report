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

import functools
import logging
import re
from typing import List

import bs4

from hqlib.typing import DateTime
from .. import url_opener
from ..abstract import owasp_dependency_report
from ..ci_server.jenkins import Jenkins


class JenkinsOWASPDependencyReport(owasp_dependency_report.OWASPDependencyReport, Jenkins):
    """ Class representing OWASP dependency reports in Jenkins jobs. """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__report_url = self.url() + "job/{job}/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/"
        self.__report_api_url = self.__report_url + self.api_postfix

        # URL for the partial OWASP dependency page listing individual files
        self.__report_html_file_list = self.__report_url + 'tab.files/'

    def _nr_warnings(self, metric_source_id: str, priority: str) -> int:
        """ Return the number of vulnerable files of the specified type in the job. """
        url = self.__report_html_file_list.format(job=metric_source_id)
        try:
            soup = self._get_soup(url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't open %s to read warning count %s: %s", url, priority, reason)
            return -1

        regex = re.compile('.*{0}.*'.format(priority.capitalize()))
        relevant_severities = soup.find_all(attrs={"tooltip": regex})
        vulnerable_files = [tag.parent.parent.find('a').text for tag in relevant_severities]
        vulnerable_file_count = len(vulnerable_files)
        logging.debug("Number of vulnerable files: %s \nList of filenames: %s", str(vulnerable_file_count),
                      str(vulnerable_files))
        return vulnerable_file_count

    def metric_source_urls(self, *job_names: str) -> List[str]:
        """ Return the url of the job. """
        return [self.__report_url.format(job=job_name) for job_name in job_names]

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date and time of one report. """
        job_url = self.url() + "job/" + metric_source_id
        return self._job_datetime(dict(url=job_url), "lastStableBuild")

    @functools.lru_cache(maxsize=1024)
    def _get_soup(self, url: str):
        """ Get a beautiful soup of the HTML at the url. """
        return bs4.BeautifulSoup(self.url_open(url), "lxml")
