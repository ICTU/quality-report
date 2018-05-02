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
from unittest.mock import patch
import urllib.error

import bs4

from hqlib.metric_source import Wiki


class WikiTest(unittest.TestCase):
    """ Unit tests for the Wiki class. """

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual("http://wiki/", Wiki("http://wiki").url())

    def test_metric_source_urls(self):
        """ Test that the metric source urls point to the team wiki pages. """
        self.assertEqual(["http://wiki/team1", "http://wiki/team2"],
                         Wiki("http://wiki").metric_source_urls("team1", "team2"))

    @patch.object(Wiki, "soup")
    def test_team_spirit(self, mock_soup):
        """ Test the spirit of the team. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr></tr><tr><td>:-)</td></tr>", "lxml")
        self.assertEqual(':-)', Wiki("http://wiki").team_spirit('team_id'))

    @patch.object(Wiki, "soup")
    def test_team_spirit_on_error(self, mock_soup):
        """ Test the spirit of the team. """
        mock_soup.side_effect = urllib.error.URLError("reason")
        self.assertEqual('', Wiki("http://wiki").team_spirit('team'))

    @patch.object(Wiki, "soup")
    def test_team_spirit_no_smiley_row(self, mock_soup):
        """ Test the spirit of the team. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr><th>18-1-2013</th></tr>", "lxml")
        self.assertEqual('', Wiki("http://wiki").team_spirit('team'))

    @patch.object(Wiki, "soup")
    def test_invalid_smiley(self, mock_soup):
        """ Test invalid smiley. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr></tr><tr><td>:-P</td></tr>", "lxml")
        self.assertEqual("", Wiki("http://wiki").team_spirit('team'))

    @patch.object(Wiki, "soup")
    def test_missing_smiley(self, mock_soup):
        """ Test missing smiley. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr></tr><tr><td></td></tr>", "lxml")
        self.assertEqual("", Wiki("http://wiki").team_spirit('team'))

    @patch.object(Wiki, "soup")
    def test_no_column_header(self, mock_soup):
        """ Test missing columns. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr><th>18-1-2013</th><th></th></tr>", "lxml")
        self.assertEqual(datetime.datetime.min, Wiki("http://wiki").datetime('team'))

    @patch.object(Wiki, "soup")
    def test_date_of_last_measurement(self, mock_soup):
        """ Test the date of the last measurement of the spirit of the team. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr><th>18-1-2013</th></tr>", "lxml")
        self.assertEqual(datetime.datetime(2013, 1, 18), Wiki("http://wiki").datetime('team'))

    @patch.object(Wiki, "soup")
    def test_date_of_last_measurement_on_error(self, mock_soup):
        """ Test the date of the last measurement of the spirit of the team when an error occurs. """
        mock_soup.side_effect = urllib.error.URLError("reason")
        self.assertEqual(datetime.datetime.min, Wiki("http://wiki").datetime('team'))

    @patch.object(Wiki, "soup")
    def test_invalid_date(self, mock_soup):
        """ Test that an invalid date is taken care of. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr><th>Datum</th><th>9-1--2013</th></tr>", "lxml")
        self.assertEqual(datetime.datetime.min, Wiki("http://wiki").datetime('team'))

    @patch.object(Wiki, "soup")
    def test_line_breaks(self, mock_soup):
        """ Test with line breaks. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr></tr><tr><td>Smiley</td><td>:-)<br/></td></tr>", "lxml")
        self.assertEqual(':-)', Wiki("http://wiki").team_spirit('team'))

    @patch.object(Wiki, "soup")
    def test_line_breaks_in_dates(self, mock_soup):
        """ Test with line breaks. """
        mock_soup.return_value = bs4.BeautifulSoup("<tr><th>Date</th><th>9-1-2018<br/></th></tr>", "lxml")
        self.assertEqual(datetime.datetime(2018, 1, 9), Wiki("http://wiki").datetime('team'))
