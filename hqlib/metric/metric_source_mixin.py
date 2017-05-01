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


import functools
from typing import List

from .. import metric_source, domain

# pylint: disable=too-few-public-methods


class SonarMetric(domain.Metric):
    """ Class for metrics that use Sonar. """
    metric_source_class = metric_source.Sonar

    @functools.lru_cache(maxsize=1024)
    def value(self):
        return super().value()

    def _is_value_better_than(self, target) -> bool:
        return super()._is_value_better_than(target)

    def _metric_source_urls(self) -> List[str]:
        """ Return the url to Sonar. """
        return [self._metric_source.url()]

    def _sonar_id(self) -> str:
        """ Return the id of the subject in Sonar. """
        return self._subject.metric_source_id(self._metric_source) or '' if self._subject else ''


class SonarDashboardMetric(SonarMetric):
    """ Class for metrics that use the Sonar dashboard. """
    def _metric_source_urls(self) -> List[str]:
        """ Return the url to the Sonar dashboard. """
        return [self._metric_source.dashboard_url(self._sonar_id())]


class SonarViolationsMetric(SonarMetric):
    """ Class for metrics that use the Sonar violations. """
    def _metric_source_urls(self) -> List[str]:
        """ Return the url to the Sonar violations. """
        return [self._metric_source.violations_url(self._sonar_id())]


class BirtTestDesignMetric(domain.Metric):
    """ Class for metrics that use the Birt test design report. """

    metric_source_class = metric_source.Birt

    @functools.lru_cache(maxsize=1024)
    def value(self):
        return super().value()

    def _is_value_better_than(self, target) -> bool:
        return super()._is_value_better_than(target)

    def _metric_source_urls(self) -> List[str]:
        """ Return the url for the What's Missing report instead of the Birt test design report since the
            What's Missing report allows users to click to the user stories and test cases in Jira. """
        return [self._metric_source.whats_missing_url()]
