"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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

# Fake objects for the measurement domain unit tests.

import datetime


class FakeHistory(object):  # pylint: disable=too-few-public-methods
    """ Class to fake the history of a metric. """
    values = []

    @classmethod
    def recent_history(cls, *args):  # pylint: disable=unused-argument
        """ Return a list of recent values. """
        return cls.values

    @staticmethod
    def status_start_date(*args):  # pylint: disable=unused-argument
        """ Return a fake start date/time. """
        return datetime.datetime(2013, 1, 1, 10, 0, 0)


class FakeWiki(object):
    """ Class to fake the wiki. """

    def __init__(self, comment=''):
        self.__comment = comment

    def comment(self, *args):  # pylint: disable=unused-argument
        """ Return a fake comment. """
        return self.__comment

    @staticmethod
    def comment_url():
        """ Return a fake url. """
        return 'http://wiki'


class FakeSubject(object):  # pylint: disable=too-few-public-methods
    """ Class to fake a metric subject. """
    def __init__(self):
        self.debt_target = None

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def technical_debt_target(self, metric_class):  # pylint: disable=unused-argument
        """ Return the technical debt target. """
        return self.debt_target
