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
        self.id = id_ or 'id'

    def get_cardslists(self):
        """ Return the lists with cards. """
        return self.__cards_lists


class FakeCardList(object):
    """ Fake a Wekan list of cards. """
    def __init__(self, cards=None):
        self.__cards = cards or []

    def get_cards(self):
        """ Return the cards on the list. """
        return self.__cards


class FakeCard(object):
    """ Fake a Wekan card. """
    id = 'card_id'

    def __init__(self, due_at=None, created_at=None, date_last_activity=None):
        self.__card_info = {}
        if due_at:
            self.__card_info["dueAt"] = due_at
        if date_last_activity:
            self.__card_info["dateLastActivity"] = date_last_activity
        self.__card_info["createdAt"] = created_at if created_at else \
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def get_card_info(self):
        """ Return the card information such as due date. """
        return self.__card_info


class WekanBoardTest(unittest.TestCase):
    """ Unit tests for the WekanBoard class. """

    def test_over_due_actions_without_overdue_cards(self):
        """ Test the number of overdue cards when there are none. """
        self.assertEqual(0, WekanBoard('', '', '', 'id', api=FakeWekanAPI([FakeBoard()])).nr_of_over_due_actions())

    def test_overdue_actions_without_board(self):
        """ Test the number of over due card whe nthere is no board. """
        self.assertEqual(-1, WekanBoard('', '', '', 'id',
                                        api=FakeWekanAPI([FakeBoard(id_='other id')])).nr_of_over_due_actions())

    def test_over_due_actions_with_overdue_cards(self):
        """ Test the number of overdue cards when there is one. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-10-24T15:52:25.249Z")])])])
        self.assertEqual(1, WekanBoard('', '', '', 'id', api=api).nr_of_over_due_actions())

    def test_over_due_actions_with_some_overdue_cards(self):
        """ Test the number of overdue cards when there are some. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-10-24T15:52:25.249Z"),
                                                     FakeCard()])])])
        self.assertEqual(1, WekanBoard('', '', '', 'id', api=api).nr_of_over_due_actions())

    def test_inactive_actions_without_cards(self):
        """ Test the number of inactive cards when there are none. """
        self.assertEqual(0, WekanBoard('', '', '', 'id', api=FakeWekanAPI([FakeBoard()])).nr_of_inactive_actions())

    def test_inactive_actions_without_board(self):
        """ Test the number of inactive card whe nthere is no board. """
        self.assertEqual(-1, WekanBoard('', '', '', 'id', api=FakeWekanAPI()).nr_of_inactive_actions())

    def test_inactive_actions_with_inactive_cards(self):
        """ Test the number of inactive cards when there is one. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(created_at="2017-1-24T15:52:25.249Z")])])])
        self.assertEqual(1, WekanBoard('', '', '', 'id', api=api).nr_of_inactive_actions())

    def test_inactive_actions_with_some_inactive_cards(self):
        """ Test the number of inactive cards when there are some. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z"),
                                                     FakeCard()])])])
        self.assertEqual(1, WekanBoard('', '', '', 'id', api=api).nr_of_inactive_actions())

    def test_inactive_actions_with_due_date_in_the_future(self):
        """ Test that cards with a due date in the future are not inactive. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z",
                                                              due_at="3000-1-1T12:00:00.000Z")])])])
        self.assertEqual(0, WekanBoard('', '', '', 'id', api=api).nr_of_inactive_actions())

    def test_over_due_actions_url(self):
        """ Test the over due actions url. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="2017-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', 'id', api=api)
        self.assertEqual({'card_id (365 dagen te laat)': 'http://wekan/b/id/title/card_id'},
                         board.over_due_actions_url(now=datetime.datetime(2018, 1, 1, 12, 0, 0)))

    def test_over_due_actions_url_without_over_due_cards(self):
        """ Test the over due actions url without over due cards. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(due_at="3000-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', 'id', api=api)
        self.assertEqual({WekanBoard.metric_source_name: 'http://wekan/b/id/title'}, board.over_due_actions_url())

    def test_over_due_actions_url_without_board(self):
        """ Test the over due actions url. """
        self.assertEqual({WekanBoard.metric_source_name: 'http://wekan'},
                         WekanBoard('http://wekan', '', '', 'id', api=FakeWekanAPI()).over_due_actions_url())

    def test_inactive_actions_url(self):
        """ Test the inactive actions url. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-1T12:00:00.000Z")])])])
        board = WekanBoard('http://wekan', '', '', 'id', api=api)
        self.assertEqual({'card_id (365 dagen niet bijgewerkt)': 'http://wekan/b/id/title/card_id'},
                         board.inactive_actions_url(now=datetime.datetime(2018, 1, 1, 12, 0, 0)))

    def test_inactive_actions_url_without_inactive_cards(self):
        """ Test the inactive actions url without inactive cards. """
        self.assertEqual({WekanBoard.metric_source_name: 'http://wekan/b/id/title'},
                         WekanBoard('http://wekan', '', '', 'id',
                                    api=FakeWekanAPI([FakeBoard()])).inactive_actions_url())

    def test_inactive_actions_url_without_board(self):
        """ Test the inactive actions url. """
        self.assertEqual({WekanBoard.metric_source_name: 'http://wekan'},
                         WekanBoard('http://wekan', '', '', 'id', api=FakeWekanAPI()).inactive_actions_url())

    def test_api_exception(self):
        """ Test that WekanBoard keeps working when the Wekan API throws an exception. """
        self.assertEqual(-1, WekanBoard('http://wekan', '', '', 'id',
                                        api=FakeWekanAPI(throw=True)).nr_of_over_due_actions())

    def test_datetime(self):
        """ Test that the WekanBoard date and time equals the most recent card change date and time. """
        api = FakeWekanAPI([FakeBoard([FakeCardList([FakeCard(date_last_activity="2017-1-24T15:52:25.249Z"),
                                                     FakeCard(due_at="2017-2-24T15:52:25.249Z")])])])
        self.assertEqual(datetime.datetime(2017, 1, 24, 15, 52, 25, 249000),
                         WekanBoard('', '', '', 'id', api=api).datetime())

    def test_datetime_without_board(self):
        """ Test the WekanBoard date and time without Wekan board. """
        self.assertEqual(datetime.datetime.min, WekanBoard('', '', '', 'id', api=FakeWekanAPI()).datetime())

    def test_datetime_without_cards(self):
        """ Test the WekanBoard date and time without Wekan board. """
        self.assertEqual(datetime.datetime.min, WekanBoard('', '', '', 'id',
                                                           api=FakeWekanAPI([FakeBoard([FakeCardList()])])).datetime())
