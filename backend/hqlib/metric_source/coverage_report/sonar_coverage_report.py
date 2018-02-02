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


from typing import Sequence

from hqlib.typing import DateTime
from ..abstract import coverage_report
from ... import metric_source


class SonarCoverageReport(coverage_report.CoverageReport):
    """ Class representing a SonarQube coverage report. """
    metric_source_name = "SonarQube coverage rapport"

    def __init__(self, sonar_url: str, *args, **kwargs) -> None:
        self.__sonar = metric_source.Sonar(sonar_url, username=kwargs.pop("username", ""),
                                           password=kwargs.pop("password", ""))
        super().__init__(*args, **kwargs)

    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        return self.__sonar.unittest_line_coverage(metric_source_id)

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        return self.__sonar.unittest_branch_coverage(metric_source_id)

    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date when the coverage for the product(s) was last successfully measured. """
        return self.__sonar.datetime(*metric_source_ids)

    def metric_source_urls(self, *metric_source_ids: str) -> Sequence[str]:
        """ Return the metric source urls for human users. """
        return [self.__sonar.dashboard_url(metric_source_id) for metric_source_id in metric_source_ids]
