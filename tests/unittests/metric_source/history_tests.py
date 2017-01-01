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

from hqlib.metric_source import History

HISTORY = ['{"date": "2013-02-28 17:16:46", "OpenBugsNone": "38", '
           '"OpenBugsFoo": ("3", "green", "2013-02-27 15:45:32"), '
           '"GreenMetaMetric": "100", "RedMetaMetric": "0", '
           '"YellowMetaMetric": "0", "GreyMetaMetric": "0", '
           '"MissingMetaMetric": "0"}\r\n']

OLD_HISTORY = ['{"date": "2013-02-27 17:16:46", '
               '"OpenBugsNone": ("35", "green", "2013-02-27 17:16:46.567"), '
               '"GreenMetaMetric": "100", "RedMetaMetric": "0", '
               '"YellowMetaMetric": "0" }\r\n']


class FakeFile(object):
    """ Fake a file object. """
    written_content = []
    initial_content = []

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        pass

    @classmethod
    def readlines(cls):
        """ Return the fake contents of the file. """
        return cls.initial_content

    @staticmethod
    def close():
        """ Fake close. """
        pass


class EmptyHistoryTest(unittest.TestCase):
    """ Unit tests for the History class with a non-existing history file. """

    def setUp(self):
        self.__history = History('non-existing file', file_=FakeFile)

    def test_no_recent_history(self):
        """ Test that there is no history when the history file does not exist. """
        self.assertEqual([], self.__history.recent_history('metric id'))

    def test_no_complete_history(self):
        """ Test that there is no history when the history file does not exist. """
        self.assertEqual([], self.__history.complete_history())


class FailingFile(FakeFile):
    """ Fake a file that raises an IO exception. """
    def __init__(self, *args, **kwargs):
        super(FailingFile, self).__init__(*args, **kwargs)
        raise IOError


class FailingFileTest(unittest.TestCase):
    """ Unit tests for the History class with a non-existing history file. """

    def setUp(self):
        self.__history = History('failing file', file_=FailingFile)

    def test_no_recent_history(self):
        """ Test that there is no history when the history file fails to open. """
        self.assertEqual([], self.__history.recent_history('metric id'))


class HistoryTest(unittest.TestCase):
    """ Unit tests for the History class with an existing history file. """

    def setUp(self):
        self.__history = History('fake file', file_=FakeFile, recent_history=3)
        FakeFile.written_content = []

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
