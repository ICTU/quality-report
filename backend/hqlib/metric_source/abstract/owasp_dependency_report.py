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

import datetime
import functools
from typing import Iterable

from hqlib.typing import DateTime
from ... import domain


class Dependency:
    """ A dependency in owasp report. """
    # pylint: disable=too-few-public-methods
    def __init__(self, file_name: str, nr_vulnerabilities: int, cve_links: list((str, str))) -> None:
        self.file_name = file_name
        self.nr_vulnerabilities = nr_vulnerabilities
        self.cve_links = cve_links


class OWASPDependencyReport(domain.MetricSource):
    """ Abstract class representing a OWASP dependency report. """
    metric_source_name = 'OWASP dependency rapport'

    def get_dependencies_info(self, metric_source_id: str, priority: str) -> list:
        """ Return info of dependencies with vulnerabilities of given priority. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def nr_warnings(self, metric_source_ids: Iterable[str], priority: str) -> int:
        """ Return the number of warnings in the reports with the specified priority. """
        warnings = [self._nr_warnings(metric_source_id, priority) for metric_source_id in metric_source_ids]
        return -1 if -1 in warnings else sum(warnings)

    def _nr_warnings(self, metric_source_id: str, priority: str) -> int:
        """ Return the  number of warnings in the report with the specified priority. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date/time of the reports. """
        results = []
        for metric_source_id in metric_source_ids:
            results.append(self._report_datetime(metric_source_id))
        return min(results) if results else datetime.datetime.min

    def _report_datetime(self, metric_source_id: str) -> DateTime:
        """ Return the date/time of one report. """
        raise NotImplementedError
