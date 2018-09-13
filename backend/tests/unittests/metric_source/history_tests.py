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
from unittest.mock import MagicMock, patch
from hqlib.metric_source import History, CompactHistory
from hqlib.persistence import JsonPersister, FilePersister


@patch.object(FilePersister, 'read_json')
class EmptyCompactHistoryTestCase(unittest.TestCase):
    """ Unit tests for the CompactHistory class when the history JSON file is empty. """

    def test_filename(self, mock_read_json):
        """ Test that the filename is correct. """
        mock_read_json.return_value = None
        history = CompactHistory('history.json')
        self.assertEqual('history.json', history.filename())

    def test_recent_history(self, mock_read_json):
        """ Test that the empty history file has no recent history. """
        mock_read_json.return_value = {"dates": [], "metrics": {}, "statuses": []}
        history = CompactHistory('history_file_name.json')

        self.assertEqual([], history.recent_history('metric id'))

    def test_long_history(self, mock_read_json):
        """ Test that the empty history file has no long history. """
        mock_read_json.return_value = {"dates": [], "metrics": {}, "statuses": []}
        history = CompactHistory('history_file_name.json')

        self.assertEqual([], history.long_history('metric id'))


DT_NOW = datetime.datetime.now()
DT_3AGO = DT_NOW - datetime.timedelta(days=3)
DT_8AGO = DT_NOW - datetime.timedelta(days=8)

DATE1 = "{y}-{m:02}-{d:02} 12:01:45".format(y=DT_8AGO.year, m=DT_8AGO.month, d=DT_8AGO.day)
DATE2 = "{y}-{m:02}-{d:02} 17:20:45".format(y=DT_3AGO.year, m=DT_3AGO.month, d=DT_3AGO.day)
DATE3 = "{y}-{m:02}-{d:02} 18:20:45".format(y=DT_3AGO.year, m=DT_3AGO.month, d=DT_3AGO.day)
DATE4 = "{y}-{m:02}-{d:02} 17:16:45".format(y=DT_NOW.year, m=DT_NOW.month, d=DT_NOW.day)

COMPACT_HISTORY = {
    "dates": [DATE1, DATE2, DATE3, DATE4],
    "metrics": {"OpenBugsNone": [
        {"value": 3,
         "start": "2017-02-28 17:01:45", "end": DATE1, "status": "yellow"},
        {"value": 10, "start": DATE2, "end": DATE2, "status": "yellow"},
        {"value": 38, "start": DATE3, "end": DATE4, "status": "red"}]},
    "statuses": [{"yellow": 1}, {"red": 1}, {"red": 1}]
}


@patch.object(FilePersister, 'read_json')
class CompactHistoryTest(unittest.TestCase):
    """ Unit tests for the History class with an existing history file. """

    def test_persister(self, mock_read_json):
        """ Test if the persister can be changed. """

        class OtherPersister(JsonPersister):
            """ Fake persister. """
            write_json = None
            read_json = MagicMock()

        CompactHistory.set_persister(OtherPersister)

        self.assertTrue(CompactHistory('history_file_path'))

        mock_read_json.assert_not_called()
        OtherPersister.read_json.assert_called_once_with('history_file_path')
        CompactHistory.set_persister(FilePersister)

    def test_filename(self, mock_read_json):
        """ Test getting the filename. """
        mock_read_json.retrun_value = '{"unimportant": "not used"}'
        history = CompactHistory('history_file_name.json')

        self.assertEqual('history_file_name.json', history.filename())

    def test_recent_history(self, mock_read_json):
        """ Test the recent history of a specific metric. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual([10, 38, 38], history.recent_history('OpenBugsNone'))

    def test_recent_history_when_metric_added_later(self, mock_read_json):
        """ Test the recent history of a specific metric. """
        history = {
            "dates": [
                "{y}-{m:02}-{d:02} 17:16:45".format(y=DT_3AGO.year, m=DT_3AGO.month, d=DT_3AGO.day),
                "{y}-{m:02}-{d:02} 17:21:45".format(y=DT_3AGO.year, m=DT_3AGO.month, d=DT_3AGO.day),
                "{y}-{m:02}-{d:02} 17:16:45".format(y=DT_NOW.year, m=DT_NOW.month, d=DT_NOW.day)
            ],
            "metrics": {"OpenBugsNone": [
                {"value": 38,
                 "start": "{y}-{m:02}-{d:02} 17:21:45".format(y=DT_3AGO.year, m=DT_3AGO.month, d=DT_3AGO.day),
                 "end": "{y}-{m:02}-{d:02} 23:59:59".format(y=DT_NOW.year, m=DT_NOW.month, d=DT_NOW.day),
                 "status": "red"}]},
            "statuses": [{"yellow": 1}, {"red": 1}, {"red": 1}]
        }

        mock_read_json.return_value = history
        history = CompactHistory('history_file_name.json')

        self.assertEqual([None, 38, 38], history.recent_history('OpenBugsNone'))

    def test_get_dates(self, mock_read_json):
        """ Test the reporting dates. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')
        self.assertEqual(DATE2 + ',' + DATE3 + ',' + DATE4, history.get_dates())

    def test_get_dates_long_limit(self, mock_read_json):
        """ Test he reporting dates are limited to 2000 for long history. """
        mock_read_json.return_value = {"dates": ["2013-02-28 17:01:45"] * 2001, "metrics": {}, "statuses": []}
        history = CompactHistory('history_file_name.json')

        self.assertEqual(','.join(['2013-02-28 17:01:45'] * 2000), history.get_dates(long_history=True))

    def test_long_history_length(self, mock_read_json):
        """ Test the length of a long history of a specific metric. """
        mock_read_json.return_value = {
            "dates": ["2013-02-28 17:01:45"] * 2001,
            "metrics": {"OpenBugsNone": [
                {"value": 10, "start": "2013-02-28 17:01:45", "end": "2013-02-28 17:01:45", "status": "yellow"},
                {"value": 38, "start": "2013-02-28 17:16:45", "end": "2013-03-05 17:16:45", "status": "red"}]},
            "statuses": [{"yellow": 1}, {"red": 1}, {"red": 1}]
        }
        history = CompactHistory('history_file_name.json')

        self.assertEqual(2000, len(history.long_history('OpenBugsNone')))

    def test_long_history(self, mock_read_json):
        """ Test the long history of a specific metric. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual([3, 10, 38, 38], history.long_history('OpenBugsNone'))

    def test_missing_recent_history(self, mock_read_json):
        """ Test the recent history of a non-existing metric. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual([], history.recent_history('Non existing'))

    def test_status_start_date(self, mock_read_json):
        """ Test that the status start date is returned correctly. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual(datetime.datetime(DT_3AGO.year, DT_3AGO.month, DT_3AGO.day, 18, 20, 45),
                         history.status_start_date('OpenBugsNone', 'red'))

    def test_statuses(self, mock_read_json):
        """ Test that the statuses are returned correctly. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual([{'yellow': 1, 'date': DATE1},
                          {'red': 1, 'date': DATE2},
                          {'red': 1, 'date': DATE3}], history.statuses())

    def test_status_start_date_no_history(self, mock_read_json):
        """ Test the status start date without history. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual(datetime.datetime(2013, 1, 1, 0, 0, 0),
                         history.status_start_date('Foo', 'red',
                                                          now=lambda: datetime.datetime(2013, 1, 1, 0, 0, 0)))

    def test_url(self, mock_read_json):
        """ Test that the url is unspecified. """
        mock_read_json.return_value = COMPACT_HISTORY
        history = CompactHistory('history_file_name.json')

        self.assertEqual("http://unspecified/", history.url())

    @patch.object(CompactHistory, 'add_metrics')
    def test_add_report(self, mock_add_metrics, mock_read_json):
        """ Test that adding a report adds the metrics."""
        mock_read_json.return_value = None
        quality_report = MagicMock()
        quality_report.date.return_value = 'quality_report.date()'
        quality_report.metrics.return_value = 'quality_report.metrics()'
        history = CompactHistory('unimportant')

        history.add_report(quality_report)

        self.assertTrue(history)
        mock_add_metrics.assert_called_once_with('quality_report.date()', 'quality_report.metrics()')

    @patch.object(FilePersister, 'write_json')
    def test_add_metrics(self, mock_write_json, mock_read_json):
        """ Test that metrics can be added. """
        mock_write_json.return_value = None
        mock_read_json.return_value = {"dates": [], "metrics": {}, "statuses": []}
        history = CompactHistory('history_file_name.json')

        class ExampleMetric(object):
            """ Fake a metric. """
            @staticmethod
            def numerical_value():
                """ Return the value. """
                return 10

            @staticmethod
            def stable_id():
                """ Return the stable metric id. """
                return 'ExampleMetric'

            @staticmethod
            def status():
                """ Return the metric status. """
                return 'green'

        history.add_metrics(datetime.datetime(2015, 1, 1), [ExampleMetric()])

        self.assertTrue(history)
        mock_write_json.assert_called_once_with(
            {
                'dates': ['2015-01-01 00:00:00'],
                'metrics': {'ExampleMetric': [
                    {'start': '2015-01-01 00:00:00', 'end': '2015-01-01 00:00:00', 'status': 'green', 'value': 10}]},
                'statuses': [{'green': 1}]
            },
            'history_file_name.json')

    @patch.object(FilePersister, 'write_json')
    def test_add_metrics_invalid_numeric(self, mock_write_json, mock_read_json):
        """ Test that a metric with numeric value -1 does not record a value. """
        mock_write_json.return_value = None
        mock_read_json.return_value = {"dates": [], "metrics": {}, "statuses": []}
        history = CompactHistory('history_file_name.json')

        class ExampleMetric(object):
            """ Fake a metric. """

            @staticmethod
            def numerical_value():
                """ Return the value. """
                return -1

            @staticmethod
            def stable_id():
                """ Return the stable metric id. """
                return 'ExampleMetric'

            @staticmethod
            def status():
                """ Return the metric status. """
                return 'green'

        history.add_metrics(datetime.datetime(2015, 1, 1), [ExampleMetric()])

        self.assertTrue(history)
        mock_write_json.assert_called_once_with(
            {
                'dates': ['2015-01-01 00:00:00'],
                'metrics': {'ExampleMetric': [
                    {'start': '2015-01-01 00:00:00', 'end': '2015-01-01 00:00:00', 'status': 'green'}]},
                'statuses': [{'green': 1}]
            }, 'history_file_name.json'
        )

    @patch.object(FilePersister, 'write_json')
    def test_add_metrics_with_previous_history(self, mock_write_json, mock_read_json):
        """ Test that a metric with a new status adds a record. """
        mock_write_json.return_value = None
        mock_read_json.return_value = {
            "dates": ["2013-02-28 17:01:45"],
            "metrics": {
                "ExampleMetric": [
                    {"value": 10, "start": "2013-02-28 17:01:45", "end": "2013-02-28 17:01:45", "status": "yellow"}
                ]
            },
            "statuses": []
        }
        history = CompactHistory('history_file_name.json')

        class ExampleMetric(object):
            """ Fake a metric. """
            @staticmethod
            def numerical_value():
                """ Return the value. """
                return 10

            @staticmethod
            def stable_id():
                """ Return the stable metric id. """
                return 'ExampleMetric'

            @staticmethod
            def status():
                """ Return the metric status. """
                return 'green'

        history.add_metrics(datetime.datetime(2015, 1, 1), [ExampleMetric()])

        self.assertTrue(history)
        mock_write_json.assert_called_once_with({
            'dates': ['2013-02-28 17:01:45', '2015-01-01 00:00:00'],
            'metrics': {'ExampleMetric': [
                {'value': 10, 'start': '2013-02-28 17:01:45', 'end': '2013-02-28 17:01:45', 'status': 'yellow'},
                {'start': '2015-01-01 00:00:00', 'end': '2015-01-01 00:00:00', 'status': 'green', 'value': 10}]},
            'statuses': [{'green': 1}]}, 'history_file_name.json')

    @patch.object(FilePersister, 'write_json')
    def test_add_metrics_with_previous_history_same_status(self, mock_write_json, mock_read_json):
        """ Test that a metric with a same status modifies existing record. """
        mock_write_json.return_value = None
        mock_read_json.return_value = {
            "dates": ["2013-02-28 17:01:45"],
            "metrics": {"ExampleMetric": [
                {"value": 10, "start": "2013-02-28 17:01:45", "end": "2013-02-28 17:01:45", "status": "green"}]},
            "statuses": [{"green": 1}]
        }
        history = CompactHistory('history_file_name.json')

        class ExampleMetric(object):
            """ Fake a metric. """
            @staticmethod
            def numerical_value():
                """ Return the value. """
                return 10

            @staticmethod
            def stable_id():
                """ Return the stable metric id. """
                return 'ExampleMetric'

            @staticmethod
            def status():
                """ Return the metric status. """
                return 'green'

        history.add_metrics(datetime.datetime(2015, 1, 1), [ExampleMetric()])

        self.assertTrue(history)
        mock_write_json.assert_called_once_with({
            'dates': ['2013-02-28 17:01:45', '2015-01-01 00:00:00'],
            'metrics': {'ExampleMetric': [
                {'value': 10, 'start': '2013-02-28 17:01:45', 'end': '2015-01-01 00:00:00', 'status': 'green'}]},
            'statuses': [{"green": 1}, {"green": 1}]}, 'history_file_name.json')


class HistoryTestCase(unittest.TestCase):
    """ Base class for History file test cases. """
    def test_if_history_is_compact_history(self):
        """ Test if instantiating of History class creates a CompactHistory object. """
        self.assertTrue(isinstance(History('unimportant'), CompactHistory))
