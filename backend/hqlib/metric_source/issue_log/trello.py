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

from typing import Any, Optional, Callable, List

from ... import utils
from ...domain import MetricSource
from ...metric_source import url_opener
from ...typing import DateTime, TimeDelta


class TrelloObject(object):
    """ Base class for Trello objects. """

    url_template = 'https://api.trello.com/1/{object_type}/{object_id}{argument}?key={appkey}&token={token}{parameters}'

    def __init__(self, appkey: str, token: str, object_id: str = '', urlopen=None) -> None:
        self._appkey = appkey
        self._token = token
        self.__object_id = object_id
        self.__urlopen = urlopen or url_opener.UrlOpener().url_open
        self.__object_type = self.__class__.__name__[len('Trello'):].lower()
        super().__init__()

    @functools.lru_cache(maxsize=1024)
    def _json(self, object_id: str = '', argument: str = '', extra_parameters: str = '') -> Any:
        """ Return the JSON at url. """
        url = self.url_template.format(
            object_type=self.__object_type, object_id=object_id or self.__object_id,
            appkey=self._appkey, token=self._token, argument=argument, parameters=extra_parameters)
        json_string = self.__urlopen(url).read()
        return utils.eval_json(json_string)

    def url(self, object_id: str = '') -> str:
        """ Return the url of a Trello object, if object id is passed, or of trello.com. """
        if object_id or self.__object_id:
            try:
                return self._json(object_id)['shortUrl']
            except url_opener.UrlOpener.url_open_exceptions:
                pass
        return 'http://trello.com'

    def datetime(self, *object_ids: str) -> DateTime:
        """ Return the date of the last action at this Trello object. """
        object_ids = object_ids or [self.__object_id]
        datetimes = []
        try:
            for object_id in object_ids:
                actions = self._json(object_id=object_id, argument='/actions', extra_parameters='&filter=all')
                if actions:
                    datetimes.append(self.date_time_from_string(actions[0]['date']))
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        return max(datetimes) if datetimes else datetime.datetime.min

    def last_update_time_delta(self, *board_ids: str) -> TimeDelta:
        """ Return the amount of time since the last update. """
        return datetime.datetime.now() - self.datetime(*board_ids)

    @staticmethod
    def date_time_from_string(date_time_timezone_string: str) -> DateTime:
        """ Parse the date/time string representation into a datetime instance. Expected format is:
            "<year>-<month>-<day>T<hour>:<minute>:<second>.<timezone>Z". """
        date_time_string = date_time_timezone_string.split('.')[0]
        year, month, day, hour, minute, second = time.strptime(date_time_string, '%Y-%m-%dT%H:%M:%S')[:6]
        return datetime.datetime(year, month, day, hour, minute, second)


class TrelloList(TrelloObject):
    """ Class representing a Trello list. """
    def name(self) -> str:
        """ Return the name of the list. """
        return self._json()["name"]


class TrelloCard(TrelloObject):
    """ Class representing a Trello card. """

    def card_id(self) -> str:
        """ Return the id of this Trello object. """
        return self._json()['idShort']

    def list_name(self) -> str:
        """ Return the name of the list that the card belongs to. """
        return TrelloList(self._appkey, self._token, self._json()["idList"]).name()

    def due_date_time(self) -> Optional[DateTime]:
        """ Return the date/time when this card is due or None when the card has no due date/time. """
        json = self._json()
        if 'due' in json:
            date_time_string = json['due']
            if date_time_string:
                return self.date_time_from_string(date_time_string)
        return None

    def over_due_time_delta(self, now: Callable[[], DateTime] = datetime.datetime.now) -> TimeDelta:
        """ Return the amount of time the card is over due. """
        due_date_time = self.due_date_time()
        return now() - due_date_time if due_date_time else datetime.timedelta()

    def is_over_due(self, now: Callable[[], DateTime] = datetime.datetime.now) -> bool:
        """ Return whether the card is over due. """
        due_date_time = self.due_date_time()
        return due_date_time < now() if due_date_time else False

    def is_inactive(self, days: int, now: Callable[[], DateTime] = datetime.datetime.now) -> bool:
        """ Return whether the card has been inactive for the specified number of days. """
        if self.due_date_time() and self.due_date_time() > now():
            return False
        max_age = datetime.timedelta(days=days)
        return now() - self.datetime() > max_age


class TrelloBoard(TrelloObject, MetricSource):
    """ Class representing a Trello board. """
    metric_source_name = 'Trello'

    def __init__(self, *args, **kwargs) -> None:
        self.__card_class = kwargs.pop('card_class', TrelloCard)
        self.__lists_to_ignore = kwargs.pop('lists_to_ignore', [])
        super().__init__(*args, **kwargs)

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        return self.__lists_to_ignore

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

    def __over_due_cards(self, *board_ids: str) -> List[TrelloCard]:
        """ Return the (non-archived) cards on this Trello board that are over due. """
        return [card for card in self.__cards(*board_ids) if card.is_over_due()]

    def __inactive_cards(self, *board_ids: str, days: int = 14) -> List[TrelloCard]:
        """ Return the (non-archived) cards on this Trello board that are inactive. """
        return [card for card in self.__cards(*board_ids) if card.is_inactive(days)]

    def over_due_cards_url(self, *board_ids: str) -> List:
        """ Return the urls for the (non-archived) cards on the Trello boards that are over due. """
        urls = list()
        try:
            for card in self.__over_due_cards(*board_ids):
                time_delta = utils.format_timedelta(card.over_due_time_delta())
                urls.append((card.url(), card.card_id(), time_delta))
        except url_opener.UrlOpener.url_open_exceptions:
            return list()
        return urls

    def inactive_cards_url(self, *board_ids: str, days: int = 14) -> List:
        """ Return the urls for the (non-archived) cards on this Trello board that are inactive. """
        urls = list()
        try:
            for card in self.__inactive_cards(*board_ids, days=days):
                time_delta = utils.format_timedelta(card.last_update_time_delta())
                urls.append((card.url(), card.card_id(), time_delta))
        except url_opener.UrlOpener.url_open_exceptions:
            return list()
        return urls

    @functools.lru_cache(maxsize=1024)
    def __cards(self, *board_ids: str) -> List[TrelloCard]:
        """ Return the (non-archived) cards on this Trello board. """
        cards = []
        try:
            for board_id in board_ids:
                cards.extend([self.__create_card(card['id']) for card in
                              self._json(object_id=board_id, argument='/cards')])
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't get cards from Trello board: %s", reason)
        return [card for card in cards if card.list_name() not in self.__lists_to_ignore]

    def __create_card(self, card_id: str) -> TrelloCard:
        """ Create a Trello card with the specified id. """
        return self.__card_class(self._appkey, self._token, card_id)

    # metric_source.MetricSource interface:

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.url(metric_source_id) for metric_source_id in metric_source_ids]

    # metric_source.ActionLog interface:

    def nr_of_over_due_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of over due cards. """
        return self.nr_of_over_due_cards(*metric_source_ids)

    def over_due_actions_url(self, *metric_source_ids: str) -> List:
        """ Return the urls to the over due cards. """
        return self.over_due_cards_url(*metric_source_ids)

    def nr_of_inactive_actions(self, *metric_source_ids: str) -> int:
        """ Return the number of inactive cards. """
        return self.nr_of_inactive_cards(*metric_source_ids)

    def inactive_actions_url(self, *metric_source_ids: str) -> List:
        """ Return the urls for the inactive cards. """
        return self.inactive_cards_url(*metric_source_ids)
