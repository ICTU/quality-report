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

import urllib.parse
import logging
from typing import Dict, Optional, Mapping, Tuple, Union

import dateutil.parser

from . import url_opener
from .. import utils
from ..domain import ExtraInfo


QueryId = Union[int, str]  # pylint: disable=invalid-name


class Jira(object):
    """ Class representing the Jira instance. """

    def __init__(self, url: str, username: str, password: str) -> None:
        self.__url = url + '/' if not url.endswith('/') else url
        self.__url_opener = url_opener.UrlOpener(username=username, password=password)
        self._extra_info = dict()

    def query_total(self, query_id: QueryId) -> int:
        """ Return the number of results of the specified query. """
        results = self.__get_query(query_id)
        return int(results['total']) if results else -1

    def _sum_for_all_issues(self, query_id: QueryId, func: callable, total: object, *args, **kwargs):
        """ Perform the func calculation over jira issues returned by the query specified by query_id. """
        results = self.__get_query(query_id)
        if not results:
            return None
        for issue in results['issues']:
            total += func(issue, *args, **kwargs)
        return total

    def average_duration_of_issues(self, query_id: QueryId) -> int:
        """ Return the average duration in days the issues were in status 'In Progress'. """
        try:
            self._extra_info[query_id] = self._sum_for_all_issues(
                query_id, self._get_days_in_progress, ExtraInfo(
                    story="Story", day_in="Begin uitvoering", day_out="Einde uitvoering",
                    days="Aantal dagen__detail-column-number", is_omitted="_detail-row-alter"))
            self._extra_info[query_id].title = 'Gemiddelde looptijd van user stories'
            days = self._sum_days_in_extra_info(self._extra_info[query_id])
            stories = self._count_stories_in_extra_info(self._extra_info[query_id])
            return days / stories if stories > 0 else -1
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.error("Error opening jira filter %s: %s.", query_id, reason)
        except ValueError:
            pass  # Error already logged in utils.eval_json
        return -1

    @staticmethod
    def _count_stories_in_extra_info(extra_info: ExtraInfo):
        return sum(not iss['is_omitted'] for iss in extra_info.data)

    @staticmethod
    def _sum_days_in_extra_info(extra_info: ExtraInfo):
        return sum(iss['days'] if not iss['is_omitted'] else 0 for iss in extra_info.data)

    def extra_info(self):
        """ Returns a list of extra infos per jira filter. """
        return list(self._extra_info.values())

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

    def _get_days_in_progress(self, issue: Dict) -> Tuple[object, str, str, Union[str, int], bool]:
        """ Fetch the changelog of the given issue and get number of days between it is moved for the first time
            to the status "In Progress", till the last time it is moved out of it. """

        issue_link = {"href": self.__url + 'browse/{key}'.format(key=issue['key']), "text": issue['fields']['summary']}

        url = self.__url + 'rest/api/2/issue/{issue_id}?expand=changelog&fields="*all,-comment"' \
            .format(issue_id=issue['key'])
        json_string = self.__url_opener.url_read(url)
        json = utils.eval_json(json_string)

        try:
            to_in_progress_date = min(self._get_create_date_from_json(json, True))
        except ValueError:
            logging.info("Invalid date, or issue %s never moved to status 'In Progress'", issue['key'])
            return issue_link, "geen", "geen", "n.v.t", True
        try:
            from_in_progress_date = max(self._get_create_date_from_json(json, False))
        except ValueError:
            logging.info("Invalid date, or issue %s still in status 'In Progress'", issue['key'])
            return issue_link, utils.format_date(to_in_progress_date, year=True), "geen", "n.v.t", True
        return issue_link, utils.format_date(to_in_progress_date, year=True), \
            utils.format_date(from_in_progress_date, year=True), \
            (from_in_progress_date - to_in_progress_date).days, False

    def query_sum(self, query_id: QueryId, field: str) -> float:
        """ Return the sum of the fields as returned by the query. """
        result = self._sum_for_all_issues(query_id, self._get_field_float_value, 0.0, field)
        return -1 if result is None else result

    @classmethod
    def _get_field_float_value(cls, issue: Dict, field: str) -> float:
        """ Get the float value from issue's field, or 0, in the case of error. """
        try:
            return float(issue['fields'][field])
        except TypeError:
            return 0

    def query_field_empty(self, query_id: QueryId, field: str) -> int:
        """ Return the number of empty fields, returned by the query. """
        result = self._sum_for_all_issues(query_id, self._increment_if_field_empty, 0, field)
        return -1 if result is None else result

    @classmethod
    def _increment_if_field_empty(cls, issue: Dict, field: str) -> float:
        """ Return 1 if the field is empty, otherwise 0. """
        try:
            int(issue['fields'][field])
            return 0
        except TypeError:
            return 1

    def __get_query(self, query_id: QueryId) -> Optional[Mapping]:
        """ Get the JSON from the query and evaluate it. """
        query_url = self.get_query_url(query_id)
        if not query_url:
            return None
        # We know that the base url configured for Jira can be used for querying so keep using that for querying
        # whatever Jira returns as scheme and netloc
        config_parts = urllib.parse.urlparse(self.__url)
        query_parts = urllib.parse.urlparse(query_url)
        read_url = config_parts.scheme + '://' + config_parts.netloc + query_parts.path + '?' + query_parts.query
        try:
            return utils.eval_json(self.__url_opener.url_read(read_url))
        except url_opener.UrlOpener.url_open_exceptions:
            return None

    def get_query_url(self, query_id: QueryId, search: bool = True) -> Optional[str]:
        """ Get the query url based on the query id. """
        if not query_id:
            return None
        url = self.__url + 'rest/api/2/filter/{qid}'.format(qid=query_id)
        try:
            json_string = self.__url_opener.url_read(url)
        except url_opener.UrlOpener.url_open_exceptions:
            return None
        url_type = 'searchUrl' if search else 'viewUrl'
        return utils.eval_json(json_string)[url_type]
