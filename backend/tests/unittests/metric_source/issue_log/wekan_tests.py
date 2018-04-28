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
import unittest

from hqlib.metric_source.issue_log.wekan import WekanBoard

# pylint: disable=too-few-public-methods


class FakeWekanAPI(object):
    """ Mock the Wekan API for unit test purposes. """

    def __init__(self, user_boards=None, throw=False):
        self.__user_boards = user_boards or []
        self.__throw = throw

    def __call__(self, *args, **kwargs):
        if self.__throw:
            raise ValueError("Something went wrong")
        else:
            return self

    def get_user_boards(self):
        """ Return the board for the user. """
        return self.__user_boards


class FakeBoard(object):
    """ Fake a Wekan board. """
    title = 'title'

    def __init__(self, cards_lists=None, id_='id'):
        self.__cards_lists = cards_lists or []
        for card_list in self.__cards_lists:
            card_list.board = self
        self.id = id_ or 'id'

    def get_cardslists(self):
        """ Return the lists with cards. """
        return self.__cards_lists


class FakeCardList(object):
    """ Fake a Wekan list of cards. """
    title = "List"

    def __init__(self, cards=None):
        self.__cards = cards or []
        for card in self.__cards:
            card.cardslist = self

    def get_cards(self):
        """ Return the cards on the list. """
        return self.__cards


class FakeCard(object):
    """ Fake a Wekan card. """
    id = 'card_id'

    def __init__(self, due_at=None, created_at=None, date_last_activity=None, start_at=None):
        self.__card_info = {}
        if due_at:
            self.__card_info["dueAt"] = due_at
        if date_last_activity:
            self.__card_info["dateLastActivity"] = date_last_activity
        if start_at:
            self.__card_info["startAt"] = start_at
        self.__card_info["createdAt"] = created_at if created_at else \
            datetime.datetime(2017, 1, 1).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def get_card_info(self):
        """ Return the card information such as due date. """
        return self.__card_info


class WekanBoardTest(unittest.TestCase):
    """ Unit tests for the WekanBoard class. """

    def test_url(self):
        """ Test the url. """
        self.assertEqual("http://wekan/",
                         WekanBoard("http://wekan/", "", "", api=FakeWekanAPI([FakeBoard()])).url())

    def test_over_due_actions_without_overdue_cards(self):
        """ Test the number of overdue cards when there are none. """
        self.assertEqual(0, WekanBoard('', '', '', api=FakeWekanAPI([FakeBoard()])).nr_of_over_due_actions('id'))

    def test_overdue_actions_without_board(self):
        """ Test the number of over due card whe nthere is no board. """
        self.assertEqual(-1, WekanBoard('', '', '',
                                        api=FakeWekanAPI([FakeBoard(id_='other id')])).nr_of_over_due_actions('id'))

    def test_over_due_actions_with_overdue_cards(self):
        """ Test the number of overdue cards when there is one. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-10-24T15:52:25.249Z")])])])
        self.assertEqual(1, WekanBoard('', '', '', api=api).nr_of_over_due_actions('id'))

    def test_over_due_actions_with_some_overdue_cards(self):
        """ Test the number of overdue cards when there are some. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-10-24T15:52:25.249Z"),
                                                     FakeCard()])])])
        self.assertEqual(1, WekanBoard('', '', '', api=api).nr_of_over_due_actions('id'))

    def test_inactive_actions_without_cards(self):
        """ Test the number of inactive cards when there are none. """
        self.assertEqual(0, WekanBoard('', '', '', api=FakeWekanAPI([FakeBoard()])).nr_of_inactive_actions('id'))

    def test_inactive_actions_without_board(self):
        """ Test the number of inactive card whe nthere is no board. """
        self.assertEqual(-1, WekanBoard('', '', '', api=FakeWekanAPI()).nr_of_inactive_actions('id'))

    def test_inactive_actions_with_inactive_cards(self):
        """ Test the number of inactive cards when there is one. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(created_at="2017-1-24T15:52:25.249Z")])])])
        self.assertEqual(1, WekanBoard('', '', '', api=api).nr_of_inactive_actions('id'))

    def test_inactive_actions_with_some_inactive_cards(self):
        """ Test the number of inactive cards when there are some. """
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z"),
                                                     FakeCard(date_last_activity=now)])])])
        self.assertEqual(1, WekanBoard('', '', '', api=api).nr_of_inactive_actions('id'))

    def test_inactive_actions_with_due_date_in_the_future(self):
        """ Test that cards with a due date in the future are not inactive. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z",
                                                              due_at="3000-1-1T12:00:00.000Z")])])])
        self.assertEqual(0, WekanBoard('', '', '', api=api).nr_of_inactive_actions('id'))

    def test_inactive_actions_with_start_date_in_the_future(self):
        """ Test that cards with a start date in the future are not inactive. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z",
                                                              start_at="3000-1-1T12:00:00.000Z")])])])
        self.assertEqual(0, WekanBoard('', '', '', api=api).nr_of_inactive_actions('id'))

    def test_over_due_actions_url(self):
        """ Test the over due actions url. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', api=api)
        self.assertEqual([('http://wekan/b/id/title/card_id', 'card_id', '365 dagen')],
                         board.over_due_actions_url('id', now=datetime.datetime(2018, 1, 1, 12, 0, 0)))

    def test_over_due_actions_url_without_over_due_cards(self):
        """ Test the over due actions url without over due cards. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="3017-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', api=api)
        self.assertEqual([], board.over_due_actions_url('id', now=datetime.datetime(2018, 1, 1, 12, 0, 0)))

    def test_over_due_actions_url_without_board(self):
        """ Test the over due actions url. """
        self.assertEqual([], WekanBoard('http://wekan', '', '', api=FakeWekanAPI()).over_due_actions_url('id'))

    def test_inactive_actions_url(self):
        """ Test the inactive actions url. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', api=api)

        self.assertEqual([('http://wekan/b/id/title/card_id', 'card_id', '365 dagen')],
                         board.inactive_actions_url('id', now=datetime.datetime(2018, 1, 1, 12, 0, 0)))

    def test_inactive_actions_url_without_inactive_cards(self):
        """ Test the inactive actions url without inactive cards. """
        self.assertEqual([], WekanBoard('http://wekan', '', '',
                                        api=FakeWekanAPI([FakeBoard()])).inactive_actions_url('id'))

    def test_inactive_actions_url_without_board(self):
        """ Test the inactive actions url. """
        self.assertEqual([], WekanBoard('http://wekan', '', '', api=FakeWekanAPI()).inactive_actions_url('id'))

    def test_api_exception(self):
        """ Test that WekanBoard keeps working when the Wekan API throws an exception. """
        self.assertEqual(-1, WekanBoard('http://wekan', '', '',
                                        api=FakeWekanAPI(throw=True)).nr_of_over_due_actions())

    def test_datetime(self):
        """ Test that the WekanBoard date and time equals the most recent card change date and time. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z"),
                                                     FakeCard(due_at="2017-2-24T15:52:25.249Z")])])])
        self.assertEqual(datetime.datetime(2017, 1, 24, 15, 52, 25, 249000),
                         WekanBoard('', '', '', api=api).datetime('id'))

    def test_datetime_without_board(self):
        """ Test the WekanBoard date and time without Wekan board. """
        self.assertEqual(datetime.datetime.min, WekanBoard('', '', '', api=FakeWekanAPI()).datetime('id'))

    def test_datetime_without_cards(self):
        """ Test the WekanBoard date and time without Wekan board. """
        self.assertEqual(datetime.datetime.min,
                         WekanBoard('', '', '', api=FakeWekanAPI([FakeBoard([FakeCardList()])])).datetime('id'))

    def test_ignore_lists(self):
        """ Test that lists can be ignored. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z")])])])
        self.assertEqual(0, WekanBoard('', '', '', lists_to_ignore=["List"], api=api).nr_of_inactive_actions('id'))

    def test_get_ignored_lists(self):
        """ Test that the ignored lists can be retrieved. """
        self.assertEqual(["List"], WekanBoard('', '', '', lists_to_ignore=["List"], api=FakeWekanAPI()).ignored_lists())
