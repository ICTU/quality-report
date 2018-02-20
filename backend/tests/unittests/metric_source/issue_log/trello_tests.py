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
import io
import urllib.error
import unittest

from unittest.mock import patch

from hqlib.metric_source.issue_log.trello import TrelloCard, TrelloList, TrelloBoard


class FakeCard(object):
    """ Fake card class to use for testing the Trello board class. """

    def __init__(self, app_key, token, card_id, *args, **kwargs):  # pylint: disable=unused-argument
        self.__card_id = card_id
        # The card id determines the status of the fake card:
        self.__over_due = card_id in (1, 3)
        self.__inactive = card_id in (2, 3)

    def card_id(self):
        """ Return the card id. """
        return self.__card_id

    def url(self):
        """ Return the card url. """
        return 'http://trello.com/api/card/{0}'.format(self.card_id())

    def is_over_due(self):
        """ Return whether this card is over due. """
        return self.__over_due

    def over_due_time_delta(self):
        """ Return how much over due the card is. """
        return datetime.timedelta(days=3 if self.__over_due else 0)

    def is_inactive(self, days):  # pylint: disable=unused-argument
        """ Return whether this card has been inactive for the specified number of days. """
        return self.__inactive

    def last_update_time_delta(self):
        """ Return the time since the last update. """
        return datetime.timedelta(days=4 if self.__inactive else 0)

    @staticmethod
    def list_name():
        """ Return the list name of the card. """
        return "List"


class TrelloBoardTest(unittest.TestCase):
    """ Unit tests for the Trello board class. """

    def setUp(self):
        self.__raise = False
        self.__cards_json = ''
        self.__trello_board = TrelloBoard('appkey', 'token', urlopen=self.__urlopen, card_class=FakeCard)

    def __urlopen(self, url):
        """ Return a fake JSON string. """
        if self.__raise:
            raise urllib.error.URLError(url)
        if 'cards' in url:
            json = self.__cards_json
        elif 'actions' in url:
            json = '[{"date": "2015-1-1T10:0:0"}]'
        else:
            json = '{{"shortUrl": "{0}", "name": "name"}}'.format(url)
        return io.StringIO(json)

    def test_url(self):
        """ Test the url of the Trello board. """
        self.assertEqual('https://api.trello.com/1/board/board_id?key=appkey&token=token',
                         self.__trello_board.url('board_id'))

    def test_over_due_cards_url(self):
        """ Test the urls for the over due cards. """
        self.__cards_json = '[{"id": 1}]'
        self.assertEqual([('http://trello.com/api/card/1', 1, '3 dagen')],
                         self.__trello_board.over_due_cards_url('board_id'))

    @patch.object(TrelloBoard, 'over_due_cards_url')
    def test_over_due_actions_url(self, mock_over_due_cards_url):
        """ Test the urls for the over due cards. """
        self.__trello_board.over_due_actions_url('board_id')
        self.assertTrue(mock_over_due_cards_url.assert_called_once)

    @patch.object(FakeCard, 'url')
    def test_over_due_cards_url_when_http_error(self, mock_url_open):
        """ Test the urls for the over due cards. """
        self.__cards_json = '[{"id": 1}]'
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual([], self.__trello_board.over_due_cards_url('board_id'))

    @patch.object(FakeCard, 'url')
    def test_inactive_cards_url_when_http_error(self, mock_url_open):
        """ Test the urls for the inactive cards. """
        self.__cards_json = '[{"id": 2}]'
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.assertEqual([], self.__trello_board.inactive_cards_url('board_id'))

    @patch.object(TrelloBoard, 'inactive_cards_url')
    def test_inactive_actions_url(self, mock_inactive_cards_url):
        """ Test the urls for the inactive cards. """
        self.__trello_board.inactive_actions_url('board_id')
        self.assertTrue(mock_inactive_cards_url.assert_called_once)

    def test_inactive_cards_url(self):
        """ Test the urls for the inactive cards. """
        self.__cards_json = '[{"id": 2}]'
        self.assertEqual([('http://trello.com/api/card/2', 2, '4 dagen')],
                         self.__trello_board.inactive_cards_url('board_id'))

    def test_last_update_delta(self):
        """ Test the time delta since last update. """
        expected = datetime.datetime.now() - datetime.datetime(2015, 1, 1, 10, 0, 0)
        actual = self.__trello_board.last_update_time_delta('board_id')
        self.assertAlmostEqual(expected.total_seconds(), actual.total_seconds(), places=2)

    def test_one_over_due(self):
        """ Test the count with one over due card. """
        self.__cards_json = '[{"id": 1}]'
        self.assertEqual(1, self.__trello_board.nr_of_over_due_cards('board_id'))
        self.assertEqual(0, self.__trello_board.nr_of_inactive_cards('board_id'))

    def test_one_inactive(self):
        """Test the count with one inactive card. """
        self.__cards_json = '[{"id": 2}]'
        self.assertEqual(1, self.__trello_board.nr_of_inactive_cards('board_id'))
        self.assertEqual(0, self.__trello_board.nr_of_over_due_cards('board_id'))

    def test_one_over_due_and_inactive(self):
        """ Test the count with one over due card. """
        self.__cards_json = '[{"id": 3}]'
        self.assertEqual(1, self.__trello_board.nr_of_over_due_cards('board_id'))
        self.assertEqual(1, self.__trello_board.nr_of_inactive_cards('board_id'))

    def test_one_inactive_and_one_over_due(self):
        """ Test the count with one inactive and one over due card. """
        self.__cards_json = '[{"id": 1}, {"id": 2}]'
        self.assertEqual(1, self.__trello_board.nr_of_over_due_cards('board_id'))
        self.assertEqual(1, self.__trello_board.nr_of_inactive_cards('board_id'))

    def test_http_error(self):
        """ Test dealing with http errors when retrieving the JSON. """
        self.__raise = True
        self.assertEqual(0, self.__trello_board.nr_of_over_due_cards('board_id'))

    def test_ignore_lists(self):
        """ Test that cards on specific lists can be ignored. """
        self.__cards_json = '[{"id": 2}]'
        board = TrelloBoard('appkey', 'token', lists_to_ignore="List", urlopen=self.__urlopen, card_class=FakeCard)
        self.assertEqual(0, board.nr_of_inactive_cards("board_id"))

    def test_get_ignored_lists(self):
        """ Test that the ignored lists can be retrieved. """
        board = TrelloBoard('appkey', 'token', lists_to_ignore=["List"], urlopen=self.__urlopen)
        self.assertEqual(["List"], board.ignored_lists())


class TrelloCardTest(unittest.TestCase):
    """ Unit tests for the Trello card class. """

    def setUp(self):
        self.__raise = False
        self.__json = '{"idShort": "id", "idList": "123"}'
        self.__trello_card = TrelloCard('object_id', 'appkey', 'token', urlopen=self.__urlopen)

    @staticmethod
    def __now():
        """ Return a fake current date time. """
        return datetime.datetime(2014, 5, 4, 17, 45, 33)

    @staticmethod
    def __earlier_now():
        """ Return a fake current date time earlier than __now(). """
        return datetime.datetime(2013, 5, 4, 17, 45, 33)

    def __urlopen(self, url):  # pylint: disable=unused-argument
        """ Return a fake JSON string. """
        return io.StringIO(self.__json)

    def test_id(self):
        """ Test the card id. """
        self.assertEqual("id", self.__trello_card.card_id())

    @patch.object(TrelloList, "name")
    def test_list_name(self, trello_list_name):
        """ Test the list name. """
        trello_list_name.return_value = "List"
        self.assertEqual("List", self.__trello_card.list_name())

    def test_no_due_date_time(self):
        """ Test that an empty card has no due date time. """
        self.assertEqual(None, self.__trello_card.due_date_time())

    def test_due_date_time(self):
        """ Test the due date time. """
        self.__json = '{"due": "2013-5-4T16:45:33.09Z"}'
        self.assertEqual(datetime.datetime(2013, 5, 4, 16, 45, 33), self.__trello_card.due_date_time())

    def test_over_due_time_delta(self):
        """ Test the age of an over due card. """
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertEqual(datetime.timedelta(hours=1), self.__trello_card.over_due_time_delta(now=self.__now))

    def test_no_over_due_time_delta(self):
        """ Test the age of a card without due date. """
        self.assertEqual(datetime.timedelta(), self.__trello_card.over_due_time_delta())

    def test_is_over_due(self):
        """ Test that an over due card is over due. """
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertTrue(self.__trello_card.is_over_due(now=self.__now))

    def test_is_not_over_due(self):
        """ Test that a card with a due date in the future is not over due. """
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertFalse(self.__trello_card.is_over_due(now=self.__earlier_now))

    def test_not_inactive_when_future_due_date(self):
        """ Test that a card with a due date in the future is not inactive. """
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertFalse(self.__trello_card.is_inactive(15, now=self.__earlier_now))

    def test_not_inactive_when_recently_updated(self):
        """ Test that a card is not inactive when it has been updated recently. """
        self.__json = '[{"date": "2014-5-4T16:45:33.09Z"}]'
        self.assertFalse(self.__trello_card.is_inactive(15, now=self.__now))


class TrelloListTest(unittest.TestCase):
    """ Unit tests for the Trello list class. """
    def setUp(self):
        self.__raise = False
        self.__json = '{"name": "List"}'
        self.__trello_list = TrelloList('object_id', 'appkey', 'token', urlopen=self.__urlopen)

    def __urlopen(self, url):  # pylint: disable=unused-argument
        """ Return a fake JSON string. """
        return io.StringIO(self.__json)

    def test_name(self):
        """ Test the name of the list. """
        self.assertEqual("List", self.__trello_list.name())
