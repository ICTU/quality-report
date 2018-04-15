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
import logging
import time

from typing import List, Optional, Tuple

from ... import utils
from ...domain import MetricSource
from ...metric_source import url_opener
from ...typing import DateTime, TimeDelta


class TrelloBoard(MetricSource):
    """ Class representing a Trello board. """
    metric_source_name = 'Trello'
    board_data_url = 'https://api.trello.com/1/boards/{object_id}/?fields=id,url,dateLastActivity&' \
                     'lists=open&list_fields=name&cards=visible&' \
                     'card_fields=shortUrl,dateLastActivity,due,idList,name&key={appkey}&token={token}'

    def __init__(self, appkey: str, token: str, *args, **kwargs) -> None:
        self._lists_to_ignore = kwargs.pop('lists_to_ignore', [])
        self.__urlopener = url_opener.UrlOpener()
        self.__appkey = appkey
        self.__token = token
        self._cards = []
        self._lists = []
        self._urls = dict()
        self._last_activity = dict()
        super().__init__(*args, **kwargs)

    def _list_ids_to_ignore(self, lists_names_to_ignore) -> List[str]:
        return [l['id'] for l in self._lists if l['name'] in lists_names_to_ignore]

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        return self._lists_to_ignore

    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date of the last action at this Trello board. """
        try:
            if not self._last_activity:
                self.__cards(*metric_source_ids)
            object_ids = metric_source_ids or self._urls.keys()
            last_board_activity_date = self.__last_board_activity_dates(object_ids)
            return max(last_board_activity_date) if last_board_activity_date else datetime.datetime.min
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't get data from Trello board: %s", reason)
            return datetime.datetime.min

    def __last_board_activity_dates(self, object_ids):
        last_board_activity_date = {
            board_id: self._last_activity[board_id] for board_id in object_ids if board_id in self._last_activity
        }.values()
        return last_board_activity_date

    def nr_of_over_due_cards(self, *board_ids: str) -> int:
        """ Return the number of (non-archived) cards on this Trello board that are over due. """
        try:
            return len(self.__over_due_cards(*board_ids))
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

    def nr_of_inactive_cards(self, *board_ids: str, days: int = 14) -> int:
        """ Return the number of (non-archived) cards on this Trello board that haven't been updated for the
            specified number of days. """
        try:
            return len(self.__inactive_cards(*board_ids, days=days))
        except url_opener.UrlOpener.url_open_exceptions:
            return -1

    def __over_due_cards(self, *board_ids: str) -> List:
        """ Return the (non-archived) cards on this Trello board that are over due. """
        return [card for card in self.__cards(*board_ids) if self.__is_card_overdue(card)]

    def __inactive_cards(self, *board_ids: str, days: int = 14) -> List:
        """ Return the (non-archived) cards on this Trello board that are inactive. """
        return [card for card in self.__cards(*board_ids) if self.__is_card_inactive(card, days)]

    def __is_card_overdue(self, card) -> bool:
        return self.__str_to_datetime(card['due']) < datetime.datetime.now() if 'due' in card and card['due'] else False

    def __is_card_inactive(self, card, days: int) -> bool:
        if 'due' in card and card['due'] and self.__str_to_datetime(card['due']) > datetime.datetime.now():
            return False
        return self.__card_last_update_time_delta(card['id']) > datetime.timedelta(days=days)

    def __card_over_due_time_delta(self, due_date_time_str: str) -> TimeDelta:
        due_date_time = self.__str_to_datetime(due_date_time_str)
        return datetime.datetime.now() - due_date_time if due_date_time else datetime.timedelta()

    def over_due_cards_url(self, *board_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls for the (non-archived) cards on the Trello boards that are over due. """
        urls = list()
        try:
            for card in self.__over_due_cards(*board_ids):
                time_delta = utils.format_timedelta(self.__card_over_due_time_delta(card['due']))
                urls.append((card['shortUrl'], card['name'], time_delta))
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't get data from Trello board: %s", reason)
            return list()
        return urls

    @staticmethod
    def __str_to_datetime(datetime_str: str) -> Optional[DateTime]:
        try:
            date_time_string = datetime_str.split('.')[0]
            year, month, day, hour, minute, second = time.strptime(date_time_string, '%Y-%m-%dT%H:%M:%S')[:6]
            return datetime.datetime(year, month, day, hour, minute, second)
        except ValueError:
            return datetime.datetime.max

    def __card_last_update_time_delta(self, card_id: str) -> TimeDelta:
        last_activity_date_strs = [c['dateLastActivity'] for c in self._cards if c['id'] == card_id]
        last_time_str = max(last_activity_date_strs) if last_activity_date_strs else ''
        return datetime.datetime.now() - self.__str_to_datetime(last_time_str if last_time_str else '')

    def inactive_cards_url(self, *board_ids: str, days: int = 14) -> List[Tuple[str, str, str]]:
        """ Return the urls for the (non-archived) cards on this Trello board that are inactive. """
        urls = list()
        try:
            for card in self.__inactive_cards(*board_ids, days=days):
                time_delta = utils.format_timedelta(self.__card_last_update_time_delta(card['id']))
                urls.append((card['shortUrl'], card['name'], time_delta))
        except url_opener.UrlOpener.url_open_exceptions:
            return list()
        return urls

    @functools.lru_cache(maxsize=1024)
    def _json_composite(self, object_id: str = '') -> None:
        """ Return the JSON at url. """
        url = self.board_data_url.format(object_id=object_id, appkey=self.__appkey, token=self.__token)
        json_string = self.__urlopener.url_read(url)
        board = utils.eval_json(json_string)
        self._cards.extend(board['cards'])
        self._lists.extend(board['lists'])
        self._urls[board['id']] = board['url']
        self._last_activity[board['id']] = self.__str_to_datetime(board['dateLastActivity'])

    @functools.lru_cache(maxsize=1024)
    def __cards(self, *board_ids: str) -> List:
        """ Return the (non-archived) cards on this Trello board. """
        if not self._cards:
            for board_id in board_ids:
                self._json_composite(object_id=board_id)
        return [card for card in self._cards if card['idList'] not in self._list_ids_to_ignore(self._lists_to_ignore)]

    # metric_source.MetricSource interface:

    def url(self, object_id: str = '') -> str:
        """ Return the url of a Trello object, if object id is passed, or of trello.com. """
        if object_id and object_id in self._urls:
            return self._urls[object_id]
        return 'http://trello.com'

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.url(metric_source_id) for metric_source_id in metric_source_ids]

    # metric_source.ActionLog interface:

    def nr_of_over_due_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of over due cards. """
        return self.nr_of_over_due_cards(*metric_source_ids)

    def over_due_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls to the over due cards. """
        return self.over_due_cards_url(*metric_source_ids)

    def nr_of_inactive_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of inactive cards. """
        return self.nr_of_inactive_cards(*metric_source_ids)

    def inactive_actions_url(self, *metric_source_ids: str) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive cards. """
        return self.inactive_cards_url(*metric_source_ids)
