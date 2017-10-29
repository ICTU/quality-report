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

from typing import Sequence

from ... import metric_source
from hqlib.typing import DateTime


class SonarTestReport(metric_source.TestReport):
    """ Metric source for retrieving (unit) test data from Sonar. """
    def __init__(self, sonar_url: str, *args, **kwargs) -> None:
        sonar_class = kwargs.pop('sonar_class', metric_source.Sonar)
        self.__sonar = sonar_class(sonar_url, username=kwargs.pop('username', ''), password=kwargs.pop('password', ''))
        super().__init__(url=sonar_url, *args, **kwargs)

    def _report_datetime(self, sonar_id: str) -> DateTime:
        return self.__sonar.datetime(sonar_id)

    def _passed_tests(self, sonar_id: str) -> int:
        """ Return the number of passed tests as reported by the test report. """
        return self.__sonar.unittests(sonar_id) - self.__sonar.failing_unittests(sonar_id)

    def _failed_tests(self, sonar_id: str) -> int:
        """ Return the number of failed tests as reported by the test report. """
        return self.__sonar.failing_unittests(sonar_id)

    def metric_source_urls(self, *metric_source_ids: str) -> Sequence[str]:
        """ Return the metric source urls for human users. """
        return [self.__sonar.dashboard_url(metric_source_id) for metric_source_id in metric_source_ids]
