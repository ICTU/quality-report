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

import datetime
import functools
import logging
from typing import Dict, Iterator, Optional

import wekanapi

from hqlib import domain, utils
from hqlib.typing import DateTime


class WekanBoard(domain.MetricSource):
    """ Wekan board used as action list and/or risk log. """

    metric_source_name = 'Wekan'

    def __init__(self, url: str, username: str, password: str, board_id: str, api=wekanapi.WekanApi) -> None:
        self.__url = url.strip('/')
        self.__username = username
        self.__password = password
        self.__board_id = board_id
        self.__wekan_api = api
        super().__init__(url=self.__url)

    # metric_source.MetricSource interface:

    def datetime(self, *metric_source_ids: str) -> DateTime:  # pylint: disable=unused-argument
        """ Return the date of the latest activity at this Wekan board. """
        if not self.__board():
            return datetime.datetime.min
        date_times = []
        for card in self.__cards():
            date_times.append(self.__last_activity(card.get_card_info()))
        return max(date_times, default=datetime.datetime.min)

    # metric_source.ActionLog interface:

    def nr_of_over_due_actions(self) -> int:
        """ Return the number of over due cards. """
        return len(list(self.__over_due_cards())) if self.__board() else -1

    def over_due_actions_url(self, now: DateTime=None) -> Dict[str, str]:
        """ Return the urls to the over due cards. """
        if not self.__board():
            return {self.metric_source_name: self.__url}
        now = now or datetime.datetime.now()
        over_due_cards = list(self.__over_due_cards(now))
        if not over_due_cards:
            return {self.metric_source_name: self.__board_url()}
        urls = {}
        for card in over_due_cards:
            time_delta = utils.format_timedelta(now - self.__due_date(card.get_card_info()))
            remark = '{time_delta} te laat'.format(time_delta=time_delta)
            label = '{card} ({remark})'.format(card=card.id, remark=remark)
            urls[label] = self.__card_url(card)
        return urls

    def nr_of_inactive_actions(self, days: int=14) -> int:
        """ Return the number of inactive cards. """
        return len(list(self.__inactive_cards(days))) if self.__board() else -1

    def inactive_actions_url(self, days: int=14, now: DateTime=None) -> Dict[str, str]:
        """ Return the urls for the inactive cards. """
        if not self.__board():
            return {self.metric_source_name: self.__url}
        now = now or datetime.datetime.now()
        inactive_cards = list(self.__inactive_cards(days, now))
        if not inactive_cards:
            return {self.metric_source_name: self.__board_url()}
        urls = {}
        for card in inactive_cards:
            time_delta = utils.format_timedelta(now - self.__last_activity(card.get_card_info()))
            remark = '{time_delta} niet bijgewerkt'.format(time_delta=time_delta)
            label = '{card} ({remark})'.format(card=card.id, remark=remark)
            urls[label] = self.__card_url(card)
        return urls

    def __board_url(self) -> str:
        """ Return the url of the board. """
        board = self.__board()
        if board:
            return self.__url + '/b/' + board.id + '/' + board.title.lower().replace(' ', '-')
        else:
            return self.__url  # pragma: no cover

    def __card_url(self, card: wekanapi.models.Card) -> str:
        """ Return the url of the card. """
        return self.__board_url() + '/' + card.id

    @functools.lru_cache(maxsize=1024)
    def __board(self) -> Optional[wekanapi.models.Board]:
        """ Return the Wekan board API. """
        try:
            api = self.__wekan_api(self.__url, credentials=dict(username=self.__username, password=self.__password))
        except Exception as reason:
            logging.error("Couldn't create API for Wekan at %s for user %s: %s", self.__url, self.__username, reason)
            return None
        for board in api.get_user_boards():
            if board.id == self.__board_id:
                return board
        logging.error("Couldn't find board with id %s at %s for user %s", self.__board_id, self.__url, self.__username)
        return None

    @classmethod
    def __due_date(cls, card_info: Dict[str, str]) -> DateTime:
        """ Return the due date of the card. """
        return cls.__parse_date_time(card_info["dueAt"]) if "dueAt" in card_info else datetime.datetime.max

    @classmethod
    def __start_date(cls, card_info: Dict[str, str]) -> DateTime:
        """ Return the start date of the card. """
        return cls.__parse_date_time(card_info["startAt"]) if "startAt" in card_info else datetime.datetime.max

    @classmethod
    def __last_activity(cls, card_info: Dict[str, str]) -> DateTime:
        """ Return the date of the last activity. """
        last_activity_field = "dateLastActivity" if "dateLastActivity" in card_info else "createdAt"
        return cls.__parse_date_time(card_info[last_activity_field])

    @staticmethod
    def __parse_date_time(date_time_string: str) -> DateTime:
        """ Parse the date time format used by Wekan. """
        return datetime.datetime.strptime(date_time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

    def __cards(self) -> Iterator[wekanapi.models.Card]:
        """ Return all cards on our board. """
        for cards_list in self.__board().get_cardslists():
            for card in cards_list.get_cards():
                yield card

    def __inactive_cards(self, days: int=14, now: DateTime=None) -> Iterator[wekanapi.models.Card]:
        """ Return all inactive cards on the board. """
        for card in self.__cards():
            if self.__is_inactive(card, days, now):
                yield card

    def __is_inactive(self, card: wekanapi.models.Card, days: int=14, now: DateTime=None) -> bool:
        """ Return whether the card is inactive. """
        now = now or datetime.datetime.now()
        info = card.get_card_info()
        if now < self.__due_date(info) < datetime.datetime.max:
            return False  # Card has a due date in the future, never consider it inactive
        if now < self.__start_date(info) < datetime.datetime.max:
            return False  # Card has a start date in the future, never consider it inactive
        return (now - self.__last_activity(info)).days > days

    def __over_due_cards(self, now: DateTime=None) -> Iterator[wekanapi.models.Card]:
        """ Return all over due cards on the board. """
        now = now or datetime.datetime.now()
        for card in self.__cards():
            info = card.get_card_info()
            if datetime.datetime.min < self.__due_date(info) < now:
                yield card
