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


from typing import List

from ..abstract.issue_tracker import BugTracker
from ...domain import ExtraInfo


class JiraFilter(BugTracker):
    """ Metric source for Jira filters. The metric source id is the filter id. """
    metric_source_name = 'Jira filter'

    def __init__(self, url: str, username: str, password: str, field_name: str = '') -> None:
        from hqlib.metric_source import Jira  # Import here to prevent circular import
        self.__jira = Jira(url, username, password)
        self.__field_name = field_name
        super().__init__()

    def nr_issues(self, *metric_source_ids: str) -> int:
        """ Return the number of issues in the filter. """
        results = [self.__jira.query_total(int(metric_source_id)) for metric_source_id in metric_source_ids]
        return -1 if -1 in results else sum(results)

    def average_duration_of_issues(self, *metric_source_ids: str) -> int:
        """ Returns average duration (in days), for stories in filter, since the begin till the end of progress. """
        results = [self.__jira.average_duration_of_issues(int(metric_source_id))
                   for metric_source_id in metric_source_ids]
        if -1 in results:
            return -1
        return sum(results) / len(results) if results else 0

    def extra_info(self) -> ExtraInfo:
        """ Method concatenates extra information for different query ids. """
        extra_infos = self.__jira.extra_info()
        result = None
        for inf in extra_infos:
            if result:
                for row in inf.data:
                    result += row.values()
            else:
                result = inf
        return result

    def nr_issues_with_field_empty(self, *metric_source_ids: str) -> int:
        """ Return the number of issues whose field has not been filled in. """
        results = [self.__jira.query_field_empty(int(metric_source_id), self.__field_name)
                   for metric_source_id in metric_source_ids]
        return -1 if -1 in results else sum(results)

    def sum_field(self, *metric_source_ids: str) -> float:
        """ Return the sum of the values in the specified field. """
        results = [self.__jira.query_sum(int(metric_source_id), self.__field_name)
                   for metric_source_id in metric_source_ids]
        return -1 if -1 in results else sum(results)

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.__jira.get_query_url(int(metric_source_id), search=False)
                for metric_source_id in metric_source_ids]
