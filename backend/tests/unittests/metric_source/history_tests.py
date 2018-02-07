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
import json
import unittest

from typing import Sequence

from hqlib.metric_source import History, CompactHistory


class FakeFile(object):  # pylint: disable=too-few-public-methods
    """ Fake a file object. """
    initial_content: Sequence[str] = []
    new_contents = ''

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        pass

    def __iter__(self):
        """ Return an iterator for the fake contents of the file. """
        return self.initial_content.__iter__()

    def read(self):
        """ Return the file contents as string. """
        return ''.join(self.initial_content)

    @classmethod
    def write(cls, data):
        """ Save the file contents as string. """
        cls.new_contents += data

    @staticmethod
    def close():
        """ Fake close. """
        pass


class EmptyCompactHistoryTestCase(unittest.TestCase):
    """ Unit tests for the CompactHistory class when the history JSON file is empty. """
    def setUp(self):
        FakeFile.initial_content = ['{"dates": [], "metrics": {}, "statuses": []}\r\n']
        self.__history = CompactHistory('history.json', file_=FakeFile)

    def test_filename(self):
        """ Test that the filename is correct. """
        self.assertEqual('history.json', self.__history.filename())

    def test_recent_history(self):
        """ Test that the empty history file has no recent history. """
        self.assertEqual([], self.__history.recent_history('metric id'))


class FailingFile(FakeFile):  # pylint: disable=too-few-public-methods
    """ Fake a file that raises an exception. """
    exception = Exception

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raise self.exception


class FailingCompactHistoryFileTest(unittest.TestCase):
    """ Unit tests for the CompactHistory class with a non-existing history file. """

    def setUp(self):
        super().setUp()
        self.__history = History('failing file', file_=FailingFile)

    def test_io_error(self):
        """ Test that there is no history when the history file fails to open. """
        FailingFile.exception = IOError
        self.assertEqual([], self.__history.recent_history('metric id'))

    def test_file_not_found(self):
        """ Test that there is no history when the history file doesn't exist. """
        FailingFile.exception = FileNotFoundError
        self.assertEqual([], self.__history.recent_history('metric id'))


COMPACT_HISTORY = ['{"dates": ["2013-02-28 17:01:45", "2013-02-28 17:16:45", "2013-03-05 17:16:45"], '
                   '"metrics": {"OpenBugsNone": [{"value": 10, "start": "2013-02-28 17:01:45", '
                   '"end": "2013-02-28 17:01:45", "status": "yellow" }, {"value": 38, "start": "2013-02-28 17:16:45", '
                   '"end": "2013-03-05 17:16:45", "status": "red"}]}, '
                   '"statuses": [{"yellow": 1}, {"red": 1}, {"red": 1}]}\r\n']


class CompactHistoryTest(unittest.TestCase):
    """ Unit tests for the History class with an existing history file. """

    def setUp(self):
        FakeFile.initial_content = COMPACT_HISTORY
        self.__history = CompactHistory('fake file', file_=FakeFile)

    def test_filename(self):
        """ Test getting the filename. """
        self.assertEqual('fake file', self.__history.filename())

    def test_recent_history(self):
        """ Test the recent history of a specific metric. """
        self.assertEqual([10, 38, 38], self.__history.recent_history('OpenBugsNone'))

    def test_missing_recent_history(self):
        """ Test the recent history of a non-existing metric. """
        self.assertEqual([], self.__history.recent_history('Non existing'))

    def test_status_start_date(self):
        """ Test that the status start date is returned correctly. """
        self.assertEqual(datetime.datetime(2013, 2, 28, 17, 16, 45),
                         self.__history.status_start_date('OpenBugsNone', 'red'))

    def test_statuses(self):
        """ Test that the statuses are returned correctly. """
        self.assertEqual([{'yellow': 1, 'date': '2013-02-28 17:01:45'},
                          {'red': 1, 'date': '2013-02-28 17:16:45'},
                          {'red': 1, 'date': '2013-03-05 17:16:45'}], self.__history.statuses())

    def test_status_start_date_no_history(self):
        """ Test the status start date without history. """
        self.assertEqual(datetime.datetime(2013, 1, 1, 0, 0, 0),
                         self.__history.status_start_date('Foo', 'red',
                                                          now=lambda: datetime.datetime(2013, 1, 1, 0, 0, 0)))

    def test_url(self):
        """ Test that the url is the filename. """
        self.assertEqual('fake file', self.__history.url())

    def test_add_metrics(self):
        """ Test that metrics can be added. """

        class FakeMetric(object):
            """ Fake a metric. """
            @staticmethod
            def numerical_value():
                """ Return the value. """
                return 10

            @staticmethod
            def stable_id():
                """ Return the stable metric id. """
                return 'FakeMetric'

            @staticmethod
            def status():
                """ Return the metric status. """
                return 'green'

        self.__history.add_metrics(datetime.datetime(2015, 1, 1), [FakeMetric()])
        history = json.loads(FakeFile.new_contents)
        self.assertEqual(10, history['metrics']['FakeMetric'][0]['value'])
        self.assertEqual('green', history['metrics']['FakeMetric'][0]['status'])


HISTORY = ['{"date": "2013-02-28 17:16:46", "OpenBugsNone": "38", '
           '"OpenBugsFoo": ("3", "green", "2013-02-27 15:45:32"), '
           '"GreenMetaMetric": "100", "RedMetaMetric": "0", '
           '"YellowMetaMetric": "0", "GreyMetaMetric": "0", '
           '"MissingMetaMetric": "0"}\r\n']

OLD_HISTORY = ['{"date": "2013-02-27 17:16:46", '
               '"OpenBugsNone": ("35", "green", "2013-02-27 17:16:46.567"), '
               '"GreenMetaMetric": "100", "RedMetaMetric": "0", '
               '"YellowMetaMetric": "0" , "MissingMetaMetric": "0", "GreyMetaMetric": "0" }\r\n']


class HistoryTestCase(unittest.TestCase):
    """ Base class for History file test cases. """
    def setUp(self):
        History._History__load_complete_history.cache_clear()
        History._History__historic_values.cache_clear()


class EmptyHistoryTest(HistoryTestCase):
    """ Unit tests for the History class with a non-existing history file. """

    def setUp(self):
        super().setUp()
        self.__history = History('non-existing file', file_=FakeFile)

    def test_no_recent_history(self):
        """ Test that there is no history when the history file does not exist. """
        self.assertEqual([], self.__history.recent_history('metric id'))


class FailingFileTest(HistoryTestCase):
    """ Unit tests for the History class with a non-existing history file. """

    def setUp(self):
        super().setUp()
        self.__history = History('failing file', file_=FailingFile)

    def test_no_recent_history(self):
        """ Test that there is no history when the history file fails to open. """
        self.assertEqual([], self.__history.recent_history('metric id'))


class HistoryTest(HistoryTestCase):
    """ Unit tests for the History class with an existing history file. """

    def setUp(self):
        super().setUp()
        self.__history = History('fake file', file_=FakeFile, recent_history=3)

    def test_filename(self):
        """ Test getting the filename. """
        self.assertEqual('fake file', self.__history.filename())

    def test_recent_history(self):
        """ Test the recent history of a specific metric. """
        FakeFile.initial_content = HISTORY
        self.assertEqual(['38'], self.__history.recent_history('OpenBugsNone'))

    def test_missing_recent_history(self):
        """ Test the recent history of a non-existing metric. """
        FakeFile.initial_content = HISTORY
        self.assertEqual([], self.__history.recent_history('Non existing'))

    def test_status_start_date(self):
        """ Test that the status start date is returned correctly. """
        FakeFile.initial_content = OLD_HISTORY
        self.assertEqual(datetime.datetime(2013, 2, 27, 17, 16, 46, 567000),
                         self.__history.status_start_date('OpenBugsNone', 'green'))

    def test_statuses(self):
        """ Test that the statuses are returned correctly. """
        FakeFile.initial_content = HISTORY
        self.assertEqual([{'green': 1, 'date': '2013-02-28 17:16:46'}], self.__history.statuses())

    def test_status_start_date_no_history(self):
        """ Test the status start date without history. """
        FakeFile.initial_content = ''
        self.assertEqual(datetime.datetime(2013, 1, 1, 0, 0, 0),
                         self.__history.status_start_date('OpenBugsNone', 'red',
                                                          now=lambda: datetime.datetime(2013, 1, 1, 0, 0, 0)))

    def test_status_start_date_new_metric(self):
        """ Test the status start date for a new metric. """
        FakeFile.initial_content = OLD_HISTORY
        self.assertEqual(datetime.datetime(2013, 1, 1, 0, 0, 0),
                         self.__history.status_start_date('NewMetric', 'red',
                                                          now=lambda: datetime.datetime(2013, 1, 1, 0, 0, 0)))

    def test_status_no_microseconds(self):
        """ Test that the status start date works without microseconds. """
        FakeFile.initial_content = HISTORY
        self.assertEqual(datetime.datetime(2013, 2, 27, 15, 45, 32),
                         self.__history.status_start_date('OpenBugsFoo', 'green'))

    def test_url(self):
        """ Test that the url is the filename. """
        self.assertEqual('fake file', self.__history.url())
