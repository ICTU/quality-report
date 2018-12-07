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

import json
import urllib.error
from urllib import parse
import datetime
import functools
import logging
from typing import List, Tuple

from hqlib import domain, utils
from hqlib.persistence import JsonPersister, FilePersister
from hqlib.typing import DateTime

from ...metric_source import url_opener


class SharepointPlanner(domain.MetricSource):
    """ Sharepoint Planner used as action list and/or risk log. """

    metric_source_name = 'Sharepoint Planner'

    # pylint: disable=too-many-arguments

    def __init__(self, url: str, client_id: str, client_secret: str,
                 refresh_token_location: str, *args, persister: JsonPersister = FilePersister, **kwargs) -> None:

        # pylint: disable=too-many-instance-attributes

        self.__url = url.strip('/')
        self.__planner_url = self.__url + '/Home/Planner'
        self.__task_display_url = self.__url + '/Home/Task/{task_id}'
        self._lists_to_ignore = kwargs.pop('lists_to_ignore', [])
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__persister = persister
        self.__refresh_token_location = refresh_token_location
        self.__tasks_url = 'https://graph.microsoft.com/v1.0/planner/plans/{plan_id}/tasks'
        self.__token_url = 'https://login.microsoftonline.com/common/oauth2/token'
        self.__access_token = self._get_access_token()
        if self.__access_token:
            self.__url_opener = url_opener.UrlOpener(authorization_token=self.__access_token)
        super().__init__(*args, **kwargs)

    def _get_access_token(self) -> str:
        refresh_token = self._load_refresh_token()
        if not refresh_token:
            return ''
        try:
            post_body = bytes(parse.urlencode({
                "grant_type": "refresh_token",
                "client_id": self.__client_id,
                "client_secret": self.__client_secret,
                "resource": "https://graph.microsoft.com",
                "refresh_token": refresh_token
            }), 'ascii')

            tokens_json = json.loads(url_opener.UrlOpener().url_read(url=self.__token_url, post_body=post_body))
            self.__persister.write_json({'refresh_token': tokens_json['refresh_token']}, self.__refresh_token_location)
            return tokens_json['access_token']
        except urllib.error.HTTPError as reason:
            logging.error('Error retrieving access token. Reason: %s. Additional information: %s',
                          reason, reason.read().decode('utf-8'))
        except json.decoder.JSONDecodeError as reason:
            logging.error('Invalid json retrieved for access token. Reason: %s.', reason)
        return ''

    def _load_refresh_token(self) -> str:
        try:
            return self.__persister.read_json(self.__refresh_token_location)['refresh_token']
        except (KeyError, TypeError) as reason:
            logging.error('Error reading refresh token. Reason: %s.', reason)
        logging.info(
            'No refresh token could be loaded. Please, generate one using the script refresh_token_generator.py.')
        return ''

    @functools.lru_cache(maxsize=8192)
    def _retrieve_tasks(self, plan_id: str) -> List:
        tasks = json.loads(self.__url_opener.url_read(url=self.__tasks_url.format(plan_id=plan_id)))['value']
        return [task for task in tasks if not task['completedDateTime']]

    def datetime(self, *metric_source_ids: str) -> DateTime:  # pylint: disable=unused-argument
        """ Return the date of the latest activity at this plan. """
        if not self.__access_token:
            return datetime.datetime.min
        try:
            return self.__get_max_activity_date(metric_source_ids)
        except url_opener.UrlOpener.url_open_exceptions:
            pass
        except (KeyError, ValueError) as reason:
            logging.error('Invalid json retrieved for tasks. Reason: %s.', reason)
        return datetime.datetime.min

    def __get_max_activity_date(self, metric_source_ids):
        last_activity_date = ''
        for plan_id in metric_source_ids:
            for task in self._retrieve_tasks(plan_id):
                last_activity_date = \
                    max(last_activity_date, task['createdDateTime'], self._get_max_assignment_date(task))
        return utils.parse_iso_datetime(last_activity_date) \
            if last_activity_date else datetime.datetime.min

    @classmethod
    def _get_max_assignment_date(cls, task: dict) -> str:
        last_assignment_date = ''
        for attr, value in task['assignments'].items():  # pylint: disable=unused-variable
            last_assignment_date = max(last_assignment_date, value['assignedDateTime'])
        return last_assignment_date

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.__planner_url]

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        return self._lists_to_ignore

    def _get_overdue_tasks(self, *metric_source_ids: str) -> List:
        return self._get_tasks_for_criterion(*metric_source_ids, criterion=self._append_task_if_overdue)

    @functools.lru_cache(maxsize=4096)
    def _get_tasks_for_criterion(self, *metric_source_ids: str, criterion) -> List:
        if self.__access_token:
            try:
                return self.__loop_through_sources_and_tasks(criterion, metric_source_ids)
            except url_opener.UrlOpener.url_open_exceptions:
                pass
            except (KeyError, ValueError) as reason:
                logging.error('Invalid json retrieved for tasks. Reason: %s.', reason)
        return None

    def __loop_through_sources_and_tasks(self, criterion, metric_source_ids):
        result = []
        dt_now = datetime.datetime.now()
        for plan_id in metric_source_ids:
            for task in self._retrieve_tasks(plan_id):
                criterion(dt_now, result, task)
        return result

    @classmethod
    def _append_task_if_overdue(cls, dt_now, result, task):
        if cls.__is_task_overdue(dt_now, task):
            result.append(task)

    def nr_of_over_due_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of over due tasks. """
        tasks = self._get_overdue_tasks(*metric_source_ids)
        return len(tasks) if tasks is not None else -1

    def over_due_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls to the over due TASKS. """
        return self._get_urls_of_tasks(*metric_source_ids,
                                       get_tasks=self._get_overdue_tasks,
                                       referent_date=lambda task: task['dueDateTime'])

    def _get_inactive_tasks(self, *metric_source_ids: str) -> List:
        return self._get_tasks_for_criterion(*metric_source_ids, criterion=self._append_tasks_if_inactive)

    def _append_tasks_if_inactive(self, dt_now, result, task):
        if self.__is_task_inactive(dt_now, task):
            result.append(task)

    @classmethod
    def __get_last_activity_date(cls, task) -> str:
        return max(task['createdDateTime'], cls._get_max_assignment_date(task))

    @classmethod
    def __is_task_inactive(cls, dt_now, task, nr_inactive_days: int = 14) -> bool:
        return (not cls.__is_task_overdue(dt_now, task)) and (dt_now - utils.parse_iso_datetime(
            cls.__get_last_activity_date(task)) > datetime.timedelta(
            days=nr_inactive_days))

    @classmethod
    def __is_task_overdue(cls, dt_now, task) -> bool:
        return 'dueDateTime' in task \
               and task['dueDateTime'] \
               and utils.parse_iso_datetime(task['dueDateTime']) < dt_now

    def nr_of_inactive_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of inactive tasks. """
        tasks = self._get_inactive_tasks(*metric_source_ids)
        return len(tasks) if tasks is not None else -1

    def inactive_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive actions. """
        return self._get_urls_of_tasks(*metric_source_ids,
                                       get_tasks=self._get_inactive_tasks,
                                       referent_date=self.__get_last_activity_date)

    def _get_urls_of_tasks(self, *metric_source_ids: str,
                           get_tasks: callable, referent_date: callable) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive actions. """
        urls = list()
        tasks = get_tasks(*metric_source_ids)
        if tasks:
            dt_now = datetime.datetime.now()
            for task in tasks:
                time_delta = utils.format_timedelta(
                    dt_now - utils.parse_iso_datetime(referent_date(task)))
                urls.append((self.__task_display_url.format(task_id=task['id']), task['title'], time_delta))
        return urls
