"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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
import datetime
from typing import List, Tuple
import dateutil.parser
from dateutil.relativedelta import relativedelta
from hqlib import utils
from hqlib.metric_source.abstract.issue_log import ActionLog
from hqlib.metric_source import JiraFilter


class JiraActionList(ActionLog):
    """ Jira used as an action list """

    metric_source_name = 'Jira Action List'

    def __init__(self, url: str, username: str, password: str, field_name: str = 'duedate', *args, **kwargs) -> None:
        self._fields_to_ignore = kwargs.pop('fields_to_ignore', [])
        self.__url = url
        self.__field_name = field_name
        self.__jira_filter = JiraFilter(self.__url, username, password, self.__field_name)
        super().__init__(*args, **kwargs)

    @classmethod
    def _is_str_date_before(cls, str_date: str, limit_date: datetime.datetime) -> bool:
        return utils.parse_iso_datetime_local_naive(str_date) < limit_date

    def _get_issues_older_than(self, *metric_source_ids: str,
                               limit_date: datetime.datetime) -> List[Tuple[str, str, str]]:
        try:
            extra_fields = ['updated', 'created'] + [list(field.keys())[0] for field in self._fields_to_ignore]
            issues = self.__jira_filter.issues_with_field_exceeding_value(
                *metric_source_ids,
                extra_fields=extra_fields,
                compare=self._is_str_date_before, limit_value=limit_date)

            return [i for i in issues if not self.__should_issue_be_ignored(i)]
        except IndexError as reason:
            logging.error("Jira filter result for overdue issues inadequate. Reason: %s.", reason)
            return None

    def __should_issue_be_ignored(self, issue) -> bool:
        for index, ignore in enumerate(self._fields_to_ignore):
            if issue[index + 5] == list(ignore.values())[0]:
                return True
        return False

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        return self._fields_to_ignore

    def nr_of_over_due_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of over due actions. """
        issue_list = self._get_issues_older_than(*metric_source_ids, limit_date=datetime.datetime.now())
        return len(issue_list) if issue_list is not None else -1

    def over_due_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls to the over due actions. """
        issue_list = self._get_issues_older_than(*metric_source_ids, limit_date=datetime.datetime.now())
        return [(issue[0], issue[1], self.__get_formatted_time_delta(issue[2])) for issue in issue_list] \
            if issue_list is not None else []

    def nr_of_inactive_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of inactive actions. """
        issue_list = self._get_issues_inactive_for(*metric_source_ids)
        return len(issue_list) if issue_list is not None else -1

    def inactive_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive actions. """
        issue_list = self._get_issues_inactive_for(*metric_source_ids)
        return [(issue[0], issue[1], self.__get_formatted_time_delta(issue[3])) for issue in issue_list] \
            if issue_list is not None else []

    def _get_issues_inactive_for(self, *metric_source_ids, delta: relativedelta = relativedelta(days=14)):
        try:
            overdue_issue_list = self._get_issues_older_than(*metric_source_ids, limit_date=datetime.datetime.now())
            return [issue for issue in overdue_issue_list if issue[3]
                    is not None and utils.parse_iso_datetime_local_naive(issue[3]) <= (datetime.datetime.now() - delta)]
        except IndexError as reason:
            logging.error("Jira filter result for inactive issues inadequate. Reason: %s.", reason)
            return None

    @classmethod
    def __get_formatted_time_delta(cls, date_to_parse) -> str:
        return utils.format_timedelta(datetime.datetime.now().astimezone() - dateutil.parser.parse(date_to_parse))

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return self.__jira_filter.metric_source_urls(*metric_source_ids)

    def datetime(self, *metric_source_ids: str) -> datetime.datetime:  # pylint: disable=unused-argument,no-self-use
        """ Return the date and time of the last measurement. """
        issue_list = self._get_issues_older_than(*metric_source_ids, limit_date=datetime.datetime.now())
        return max([max(utils.parse_iso_datetime_local_naive(issue[4]),
                        utils.parse_iso_datetime_local_naive(issue[3]) if issue[3] else datetime.datetime.min)
                    for issue in issue_list])
