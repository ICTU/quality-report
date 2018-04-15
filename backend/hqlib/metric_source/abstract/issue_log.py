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


from typing import List, Tuple

from ... import domain


class IssueLog(domain.MetricSource):
    """ Abstract based class for issues logs. """
    metric_source_name = 'Issue log'

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        raise NotImplementedError


class RiskLog(IssueLog):
    """ Abstract base class for risk logs. """
    metric_source_name = 'Risk log'

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        raise NotImplementedError


class ActionLog(IssueLog):
    """ Abstract base class for action logs. """
    metric_source_name = 'Action log'

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        raise NotImplementedError

    def nr_of_over_due_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of over due actions. """
        raise NotImplementedError

    def over_due_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls to the over due actions. """
        raise NotImplementedError

    def nr_of_inactive_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of inactive actions. """
        raise NotImplementedError

    def inactive_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive actions. """
        raise NotImplementedError
