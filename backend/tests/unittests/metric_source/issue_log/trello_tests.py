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
import urllib.error
import unittest

from unittest.mock import patch

from hqlib.metric_source import url_opener
from hqlib.metric_source.issue_log.trello import TrelloBoard


class TrelloBoardTest(unittest.TestCase):
    """ Unit tests for the Trello board class. """

    def test_ignored_lists(self):
        """ Test the ignored lists are initialised correctly. """
        ignored_lists = ['A list name']
        trello_board = TrelloBoard('unimportant', 'unimportant', lists_to_ignore=ignored_lists)

        self.assertEqual(ignored_lists, trello_board.ignored_lists())

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_no_board_date_last_activity(self, mock_url_read):
        """ Test the board datetime is correctly filled and returned. """
        mock_url_read.return_value = '{"id": "board_id", "url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertRaises(KeyError, lambda: trello_board.datetime('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime(self, mock_url_read):
        """ Test the board datetime is correctly filled and returned. """
        mock_url_read.return_value = '{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        result = trello_board.datetime('board_id')

        self.assertEqual(datetime.datetime(2018, 3, 5, 11), result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_(self, mock_url_read):
        """ Test the board datetime when incorrect board id is given. """
        mock_url_read.return_value = '{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')
        trello_board.over_due_cards_url('board_id')

        result = trello_board.datetime('id_of_not_retrieved_board')

        self.assertEqual(datetime.datetime.min, result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_already_filled(self, mock_url_read):
        """ Test the board datetime is correctly returned when it is pre-filled by other action."""
        mock_url_read.return_value = '{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')
        trello_board.over_due_cards_url('board_id')

        result = trello_board.datetime()

        mock_url_read.asses_called_once()
        self.assertEqual(datetime.datetime(2018, 3, 5, 11), result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_two_boards(self, mock_url_read):
        """ Test the datetime returns the last day of activity of all retrieved boards. """
        mock_url_read.side_effect = ['{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", '
                                     '"url": "https://xxx", "lists": [], "cards": []}',
                                     '{"id": "b2_id", "dateLastActivity":"2018-03-06T11:00:00.000Z", '
                                     '"url": "https://xxx", "lists": [], "cards": []}']
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        result = trello_board.datetime('board_id', 'b2_id')

        self.assertEqual(datetime.datetime(2018, 3, 6, 11), result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_datetime_http_error(self, mock_url_read):
        """ Test the datetime returns the last day of activity of all retrieved boards. """
        mock_url_read.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        result = trello_board.datetime('board_id', 'b2_id')

        self.assertEqual(datetime.datetime.min, result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_url(self, mock_url_read):
        """ Test the url of the Trello board. """
        mock_url_read.return_value = '{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')
        trello_board.over_due_cards_url('board_id')

        self.assertEqual('https://xxx', trello_board.url('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_url_empty_board_id(self, mock_url_read):
        """ Test the Trello board returns the default url, when empty board id is provided. """
        mock_url_read.return_value = '{"id": "board_id", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "https://xxx", "lists": [], "cards": []}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')
        trello_board.over_due_cards_url('board_id')

        self.assertEqual('http://trello.com', trello_board.url(''))

    def test_url_not_retrieved(self):
        """ Test the Trello board returns the default url, when no card retrieval is done. """
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertEqual('http://trello.com', trello_board.url('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_cards(self, mock_url_read):
        """ Test the card with the due in the past is considered as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"due": "2018-03-05T11:00:00.000Z"}]}'
            self.trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = self.trello_board.nr_of_over_due_cards('board_id')

        self.assertEqual(1, result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_over_due_cards_when_http_error(self, mock_url_open):
        """ Test that when there is an HTTP error during retrieval, it returns an empty list as overdue cards. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertEqual(-1, trello_board.nr_of_over_due_cards('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url(self, mock_url_read):
        """ Test the card with the due in the past is considered as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"due": "2018-03-05T11:00:00.000Z"}]}'
            self.trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = self.trello_board.over_due_cards_url('board_id')

        self.assertEqual([('http://shortUrl', "Test card!", '3 dagen')], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_fetches_only_once(self, mock_url_read):
        """ Test the calls on trello board are repeatable without retrieving data again. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"due": "2018-03-05T11:00:00.000Z"}]}'
            self.trello_board = TrelloBoard('appkeyX', 'tokenX')

            result1 = self.trello_board.over_due_cards_url('board_id')
            result2 = self.trello_board.over_due_cards_url('board_id')

        mock_url_read.assert_called_once()
        self.assertEqual([('http://shortUrl', "Test card!", '3 dagen')], result1)
        self.assertEqual(result1, result2)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_when_due_null(self, mock_url_read):
        """ Test the card with a null due date is not considered as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl", "due": null}]}'
            self.trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = self.trello_board.over_due_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_when_not_overdue(self, mock_url_read):
        """ Test the card with the due in the future is not considered as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"due": "2018-03-10T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.over_due_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_without_due_date(self, mock_url_read):
        """ Test the card without a due date is not considered as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"idList": "xx", ' \
                                         '"name": "Test card!", "shortUrl": "http://shortUrl"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.over_due_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_when_empty(self, mock_url_read):
        """ Test that when there are no cards at all it returns an empty list as overdue. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": []}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.over_due_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_when_list_excluded(self, mock_url_read):
        """ Test excludes cards belonging to the ignored lists. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [{"id": "list_id", "name": "Excluded"}], ' \
                                         '"cards": [{"idList": "list_id", "name": "Test card!", ' \
                                         '"shortUrl": "http://shortUrl", "due": "2018-03-05T11:00:00.000Z"}]}'
            self.trello_board = TrelloBoard('appkeyX', 'tokenX', lists_to_ignore=['Excluded'])

            result = self.trello_board.over_due_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_over_due_cards_url_when_http_error(self, mock_url_open):
        """ Test that when there is an HTTP error during retrieval, it returns an empty list as overdue cards. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertEqual([], trello_board.over_due_cards_url('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_cards(self, mock_url_read):
        """ Test the inactive card for exactly 14 days. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-06T11:00:00.000Z", "due": null}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.nr_of_inactive_cards('board_id')

        self.assertEqual(1, result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_nr_of_inactive_cards_when_http_error(self, mock_url_open):
        """ Test that when there is an HTTP error during retrieval, it returns an empty list as overdue cards. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertEqual(-1, trello_board.nr_of_inactive_cards('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_when_http_error(self, mock_url_open):
        """ Test that when there is an HTTP error during retrieval, it returns an empty list as inactive cards. """
        mock_url_open.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertEqual([], trello_board.inactive_cards_url('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_when_empty(self, mock_url_read):
        """ Test that when there are no cards at all it returns an empty list as inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 9)
            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": []}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url(self, mock_url_read):
        """ Test the inactive card for exactly 14 days. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-06T11:00:00.000Z", "due": null}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([('http://shortUrl', "Test card!", '14 dagen')], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_with_last_activity_null(self, mock_url_read):
        """ Test that the card with dateLastActivity equal to null is not counted as inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.max = datetime.max

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": null, "due": null}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_without_last_activity(self, mock_url_read):
        """ Test that it raises key error exception when there is no dateLastActivity. """

        mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                     '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                     '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", "due": null}]}'
        trello_board = TrelloBoard('appkeyX', 'tokenX')

        self.assertRaises(KeyError, lambda: trello_board.inactive_cards_url('board_id'))

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_custom_term(self, mock_url_read):
        """ Test the card is considered active or inactive according to the custom interval. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-06T11:00:00.000Z", "due": null}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id', days=15)

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_more_boards(self, mock_url_read):
        """ Test the inactive cards of more than one board are returned together. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.side_effect = ['{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", '
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": '
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", '
                                         '"dateLastActivity": "2018-03-05T11:00:00.000Z"}]}',
                                         '{"id": "x2", "dateLastActivity":"2018-03-05T11:00:00.000Z", '
                                         '"url": "", "lists": [], "cards": [{"id": "card_2", "idList": '
                                         '"l2", "name": "Card 2", "shortUrl": "http://shortUrl2", '
                                         '"dateLastActivity": "2018-03-01T11:00:00.000Z"}]}']
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('x', 'x2')

        self.assertEqual([('http://shortUrl', "Test card!", '15 dagen'),
                          ('http://shortUrl2', "Card 2", '19 dagen')], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_less_than_14_days(self, mock_url_read):
        """ Test that the cards inactive for less than default 14 days are not considered inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-15T11:00:00.000Z", "due": null}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_invalid_due_date(self, mock_url_read):
        """ Test the cards with invalid due date are not considered inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.max = datetime.max

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-05T11:00:00.000Z", ' \
                                         '"due": "2018-99-77T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_invalid_last_activity_date(self, mock_url_read):
        """ Test the cards without due date and invalid last activity date are not considered inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.max = datetime.max

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-99-88T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_less_without_due_date(self, mock_url_read):
        """ Test the urls for the over due cards. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-15T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_still_not_due(self, mock_url_read):
        """ Test that the card that is still not due is not considered inactive, regardless of last activity date. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-05T11:00:00.000Z", ' \
                                         '"due": "2018-03-22T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([], result)

    @patch.object(url_opener.UrlOpener, 'url_read')
    def test_inactive_cards_url_already_due(self, mock_url_read):
        """ Test the card already due and with last activity before (default) 14 days is considered as inactive. """
        from datetime import datetime
        with patch(__name__ + '.datetime.datetime') as mock_date:
            mock_date.now.return_value = datetime(2018, 3, 21)
            mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_url_read.return_value = '{"id": "x", "dateLastActivity":"2018-03-05T11:00:00.000Z", ' \
                                         '"url": "", "lists": [], "cards": [{"id": "card_id", "idList": ' \
                                         '"xx", "name": "Test card!", "shortUrl": "http://shortUrl", ' \
                                         '"dateLastActivity": "2018-03-05T11:00:00.000Z", ' \
                                         '"due": "2018-03-20T11:00:00.000Z"}]}'
            trello_board = TrelloBoard('appkeyX', 'tokenX')

            result = trello_board.inactive_cards_url('board_id')

        self.assertEqual([('http://shortUrl', "Test card!", '15 dagen')], result)

    @patch.object(TrelloBoard, 'over_due_cards_url')
    def test_over_due_actions_url(self, mock_over_due_cards_url):
        """ Test the over_due_actions_url is alias for over_due_cards_url. """
        TrelloBoard('appkeyX', 'tokenX').over_due_actions_url('board_id')
        self.assertTrue(mock_over_due_cards_url.assert_called_once)

    @patch.object(TrelloBoard, 'inactive_cards_url')
    def test_inactive_actions_url(self, mock_inactive_cards_url):
        """ Test the inactive_actions_url is alias for inactive_cards_url. """
        TrelloBoard('appkeyX', 'tokenX').inactive_actions_url('board_id')
        self.assertTrue(mock_inactive_cards_url.assert_called_once)

    @patch.object(TrelloBoard, 'nr_of_over_due_cards')
    def test_nr_of_over_due_actions(self, mock_over_due_cards_url):
        """ Test the nr_of_over_due_actions is alias for nr_of_over_due_cards. """
        TrelloBoard('appkeyX', 'tokenX').nr_of_over_due_actions('board_id')
        self.assertTrue(mock_over_due_cards_url.assert_called_once)

    @patch.object(TrelloBoard, 'nr_of_inactive_cards')
    def test_nr_of_inactive_actions(self, mock_inactive_cards_url):
        """ Test the nr_of_inactive_actions is alias for nr_of_inactive_cards. """
        TrelloBoard('appkeyX', 'tokenX').nr_of_inactive_actions('board_id')
        self.assertTrue(mock_inactive_cards_url.assert_called_once)
