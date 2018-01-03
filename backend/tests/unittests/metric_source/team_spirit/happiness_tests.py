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
import urllib.error

from hqlib.metric_source import Happiness


class Opener(object):  # pylint: disable=too-few-public-methods
    """ Override the url_open method to return a fixed HTML fragment. """
    json = """[{"datum":"2016-08-29","smiley":"4"},{"datum":"2016-09-22","smiley":"3"}]"""

    def url_read(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        if 'raise' in url:
            raise urllib.error.HTTPError(None, None, None, None, None)
        else:
            return self.json


class HappinessTest(unittest.TestCase):
    """ Unit tests for the Happiness class. """

    def setUp(self):
        self.__happiness = Happiness('http://opener/', url_read=Opener().url_read)

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://opener/', self.__happiness.url())

    def test_team_spirit(self):
        """ Test the spirit of the team. """
        self.assertEqual(':-|', self.__happiness.team_spirit('team_2'))

    def test_missing_team_spirit(self):
        """ Test the spirit when an error is raised. """
        self.assertEqual('', Happiness('raise', url_read=Opener().url_read).team_spirit('team'))

    def test_date_of_last_measurement(self):
        """ Test the date of the last measurement of the spirit of the team. """
        self.assertEqual(datetime.datetime(2016, 9, 22),
                         self.__happiness.datetime('team_2'))

    def test_missing_date_of_last_measurement(self):
        """ Test the date when an error is raised. """
        self.assertEqual(datetime.datetime.min,
                         Happiness('raise', url_read=Opener().url_read).datetime('team'))

    def test_team_spirit_wrong_smiley(self):
        """ Test the spirit when the smiley isn't recognized. """
        opener = Opener()
        opener.json = """[{"datum":"2016-09-22","smiley":"0"}]"""
        self.assertEqual('', Happiness('http://opener/', url_read=opener.url_read).team_spirit('team'))

    def test_date_without_data(self):
        """ Test the date when there haven't been any smileys registered. """
        opener = Opener()
        opener.json = """[{}]"""
        self.assertEqual(datetime.datetime.min,
                         Happiness('http://opener', url_read=opener.url_read).datetime('team'))
