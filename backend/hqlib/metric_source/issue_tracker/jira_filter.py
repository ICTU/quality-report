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

import logging
from typing import Callable, List, Dict, Tuple, Union, Optional
import dateutil.parser
from hqlib import utils
from hqlib.typing import DateTime
from ..abstract.issue_tracker import BugTracker

QueryId = Union[int, str]  # pylint: disable=invalid-name


class JiraFilter(BugTracker):
    """ Metric source for Jira filters. The metric source id is the filter id. """
    metric_source_name = 'Jira filter'

    def __init__(self, url: str, username: str, password: str, field_name: str = '') -> None:
        from hqlib.metric_source import Jira  # Import here to prevent circular import
        self.__url = url
        self.__jira = Jira(url, username, password)
        self.__field_name = field_name
        super().__init__()

    def _query_field_empty(self, query_id: QueryId, field: str) -> Tuple[int, List[str]]:
        """ Return the number of empty fields, returned by the query. """
        return self.__query_field(query_id, self._increment_if_field_empty, field)

    def __query_field(self, query_id: QueryId, func: Callable, field: str) -> Tuple[int, List[str]]:
        """ Return the number of empty fields, returned by the query. """
        result = self.sum_for_all_issues(query_id, func, tuple(), field)
        return (-1, []) if result is None else (sum(result[::2]), self._get_just_links(result[1::2]))

    @classmethod
    def _increment_if_field_empty(cls, issue: Dict, field: str) -> Tuple:
        """ Return 1 if the field is empty, otherwise 0. """
        try:
            int(issue['fields'][field])
            return 0, None
        except (TypeError, KeyError):
            return 1, issue

    def _query_total(self, query_id: QueryId) -> Tuple[int, List[str]]:
        """ Return the number of results of the specified query. """
        results = self.__jira.get_query(query_id)
        return (int(results['total']), self._get_just_links(results['issues'])) if results else (-1, [])

    def _get_just_links(self, issues: List):
        return [
            utils.format_link_object(
                self.get_issue_url(issue['key']),
                issue['fields']['summary'])
            for issue in issues if issue]

    def nr_issues(self, *metric_source_ids: str) -> Tuple[int, List[str]]:
        """ Return the number of issues in the filter. """
        count, issues = zip(*[self._query_total(int(metric_source_id)) for metric_source_id in metric_source_ids])
        return -1 if -1 in count else sum(count), issues[0]

    @classmethod
    def _get_create_date_from_json(cls, json: Dict, to_str: bool):
        to_from = "toString" if to_str else "fromString"

        def is_progress_event(history_item):
            """ Return whether the history item is a start of progress or end of progress event. """
            return history_item["field"] == "status" and history_item["fieldtype"] == "jira" and \
                history_item[to_from] == "In Progress"

        dates = []
        for history in json['changelog']['histories']:
            if any(filter(is_progress_event, history['items'])):
                dates.append(dateutil.parser.parse(history["created"]))
        return dates

    def get_start_and_end_progress_date(self, issue: Dict) -> Tuple[Optional[DateTime], Optional[DateTime]]:
        """ Fetch the changelog of the given issue and get number of days between it is moved for the first time
            to the status "In Progress", till the last time it is moved out of it. """
        json = self.__jira.get_issue_details(issue['key'])
        try:
            to_in_progress_date = min(self._get_create_date_from_json(json, True))
        except ValueError:
            logging.info("Invalid date, or issue %s never moved to status 'In Progress'", issue['key'])
            return None, None
        except TypeError:
            logging.error("Received invalid json from %s: %s", self.__url, json)
            return None, None
        try:
            from_in_progress_date = max(self._get_create_date_from_json(json, False))
        except ValueError:
            logging.info("Invalid date, or issue %s still in status 'In Progress'", issue['key'])
            return to_in_progress_date, None
        return to_in_progress_date, from_in_progress_date

    def sum_for_all_issues(self, query_id: QueryId, func: Callable, total: object, *args, **kwargs):
        """ Perform the func calculation over jira issues returned by the query specified by query_id. """
        results = self.__jira.get_query(query_id)
        if not results:
            return None
        for issue in results['issues']:
            total += func(issue, *args, **kwargs)
        return total

    def get_issue_url(self, issue_key: str) -> str:
        """ Format Jira issue url for given issue id. """
        return self.__url + 'browse/{key}'.format(key=issue_key)

    def nr_issues_with_field_empty(self, *metric_source_ids: str) -> Tuple[int, List[str]]:
        """ Return the number of issues whose field has not been filled in. """
        count, issues = zip(*[
            self._query_field_empty(int(metric_source_id), self.__field_name)
            for metric_source_id in metric_source_ids])
        return -1 if -1 in count else sum(count), issues[0]

    def issues_with_field(self, *metric_source_ids: str) -> List[Tuple[str, float]]:
        """ Return a list of issues links and values from the specified field. """
        links_and_values = []
        for query_id in metric_source_ids:
            query_result = self.__jira.get_query(query_id)
            try:
                issues = query_result["issues"]
            except (ValueError, KeyError, TypeError) as reason:
                logging.error("Couldn't get issues from Jira filter %s: %s", query_id, reason)
                return []
            for issue in issues:
                fields = issue["fields"]
                if not fields.get(self.__field_name):
                    continue  # Skip issues that don't have a value for the field
                link = utils.format_link_object(self.get_issue_url(issue["key"]), fields["summary"])
                links_and_values.append((link, float(fields[self.__field_name])))
        return links_and_values

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.__jira.get_query_url(int(metric_source_id), search=False)
                for metric_source_id in metric_source_ids]
