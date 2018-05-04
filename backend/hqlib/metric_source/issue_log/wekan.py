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
from typing import Dict, Iterator, List, Sequence, Tuple

import wekanapi

from hqlib import domain, utils
from hqlib.typing import DateTime


class WekanBoard(domain.MetricSource):
    """ Wekan board used as action list and/or risk log. """

    metric_source_name = 'Wekan'

    def __init__(self, url: str, username: str, password: str, lists_to_ignore=None, api=wekanapi.WekanApi) -> None:
        self.__url = url.strip('/')
        self.__username = username
        self.__password = password
        self.__lists_to_ignore = lists_to_ignore or []
        self.__wekan_api = api
        super().__init__(url=self.__url)

    # metric_source.MetricSource interface:

    def datetime(self, *board_ids: str) -> DateTime:  # pylint: disable=unused-argument
        """ Return the date of the latest activity at this Wekan board. """
        date_times = [self.__last_activity(card.get_card_info()) for card in self.__cards(*board_ids)]
        return max(date_times, default=datetime.datetime.min)

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Convert board ids to urls. """
        return self.__board_urls(*metric_source_ids)

    # metric_source.ActionLog interface:

    def ignored_lists(self) -> List[str]:
        """ Return the ignored lists. """
        return self.__lists_to_ignore

    def nr_of_over_due_actions(self, *board_ids: str) -> int:
        """ Return the number of over due cards. """
        return len(list(self.__over_due_cards(*board_ids))) if self.__boards(*board_ids) else -1

    def over_due_actions_url(self, *board_ids: str, now: DateTime = None) -> List[Tuple[str, str, str]]:
        """ Return the urls to the over due cards. """
        if not self.__boards(*board_ids):
            return list()
        now = now or datetime.datetime.now()
        over_due_cards = list(self.__over_due_cards(*board_ids, now=now))
        if not over_due_cards:
            return list()
        urls = list()
        for card in over_due_cards:
            time_delta = utils.format_timedelta(now - self.__due_date(card.get_card_info()))
            urls.append((self.__card_url(card), card.id, time_delta))
        return urls

    def nr_of_inactive_actions(self, *board_ids: str, days: int = 14) -> int:
        """ Return the number of inactive cards. """
        return len(list(self.__inactive_cards(*board_ids, days=days))) if self.__boards(*board_ids) else -1

    def inactive_actions_url(self, *board_ids: str, days: int = 14, now: DateTime = None) -> List[Tuple[str, str, str]]:
        """ Return the urls for the inactive cards. """
        if not self.__boards(*board_ids):
            return list()
        now = now or datetime.datetime.now()
        inactive_cards = list(self.__inactive_cards(*board_ids, days=days, now=now))
        if not inactive_cards:
            return list()
        urls = list()
        for card in inactive_cards:
            time_delta = utils.format_timedelta(now - self.__last_activity(card.get_card_info()))
            urls.append((self.__card_url(card), card.id, time_delta))
        return urls

    def __board_urls(self, *board_ids: str) -> List[str]:
        """ Return the urls of the boards. """
        urls = []
        for board in self.__boards(*board_ids):
            urls.append(self.__url + '/b/' + board.id + '/' + board.title.lower().replace(' ', '-'))
        return urls if urls else [self.__url]

    def __card_url(self, card: wekanapi.models.Card) -> str:
        """ Return the url of the card. """
        return self.__board_urls(card.cardslist.board.id)[0] + '/' + card.id

    @functools.lru_cache(maxsize=1024)
    def __boards(self, *board_ids: str) -> Sequence[wekanapi.models.Board]:
        """ Return the boards for the specified board ids. Will returns an empty sequence if one of the
            boards cannot be found. """
        try:
            api = self.__wekan_api(self.__url, credentials=dict(username=self.__username, password=self.__password))
        except Exception as reason:
            logging.warning("Couldn't create API for Wekan at %s for user %s: %s", self.__url, self.__username, reason)
            return []
        boards = []
        for board in api.get_user_boards():
            if board.id in board_ids:
                boards.append(board)
        if not boards:
            logging.warning("Couldn't find boards with ids %s at %s for user %s", board_ids, self.__url,
                            self.__username)
        return boards

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

    def __cards(self, *board_ids: str) -> Iterator[wekanapi.models.Card]:
        """ Return all cards on the boards. """
        for board in self.__boards(*board_ids):
            for cards_list in board.get_cardslists():
                if cards_list.title in self.__lists_to_ignore:
                    continue
                for card in cards_list.get_cards():
                    yield card

    def __inactive_cards(self, *board_ids: str, days: int = 14, now: DateTime = None) -> Iterator[wekanapi.models.Card]:
        """ Return all inactive cards on the boards. """
        for card in self.__cards(*board_ids):
            if self.__is_inactive(card, days, now):
                yield card

    def __is_inactive(self, card: wekanapi.models.Card, days: int = 14, now: DateTime = None) -> bool:
        """ Return whether the card is inactive. """
        now = now or datetime.datetime.now()
        info = card.get_card_info()
        if now < self.__due_date(info) < datetime.datetime.max:
            return False  # Card has a due date in the future, never consider it inactive
        if now < self.__start_date(info) < datetime.datetime.max:
            return False  # Card has a start date in the future, never consider it inactive
        return (now - self.__last_activity(info)).days > days

    def __over_due_cards(self, *board_ids: str, now: DateTime = None) -> Iterator[wekanapi.models.Card]:
        """ Return all over due cards on the boards. """
        now = now or datetime.datetime.now()
        for card in self.__cards(*board_ids):
            info = card.get_card_info()
            if datetime.datetime.min < self.__due_date(info) < now:
                yield card
