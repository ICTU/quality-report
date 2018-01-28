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

import bs4

from hqlib.metric_source import Wiki


class WikiUnderTest(Wiki):  # pylint: disable=too-few-public-methods
    """ Override the soup method to return a fixed HTML fragment. """
    html = """<table border="1">
                <tr>
                  <th align="right">Datum</th>
                  <th>9-1-2013</th>
                  <th>18-1-2013</th>
                </tr>
                <tr id="team_1">
                    <td>Smiley team 1</td>
                    <td></td><td>:-)</td>
                </tr>
                <tr id="team_2">
                    <td>Smiley 2</td>
                    <td>:-)</td>
                    <td>:-(</td>
                </tr>
              </table>"""

    def soup(self, url):  # pylint: disable=unused-argument
        """ Return the static html. """
        return bs4.BeautifulSoup(self.html, "lxml")


class WikiTest(unittest.TestCase):
    """ Unit tests for the Wiki class. """

    def setUp(self):
        self.__wiki = WikiUnderTest('http://wiki')

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual('http://wiki', self.__wiki.url())

    def test_metric_source_urls(self):
        """ Test that the metric source urls are simply the Wiki url. """
        self.assertEqual(["http://wiki"], self.__wiki.metric_source_urls("team1", "team2"))

    def test_team_spirit(self):
        """ Test the spirit of the team. """
        self.assertEqual(':-(', self.__wiki.team_spirit('team_2'))

    def test_missing_team_spirit(self):
        """ Test exception when team is missing. """
        self.assertEqual('', self.__wiki.team_spirit('missing'))

    def test_no_column_header(self):
        """ Test missing columns. """
        self.__wiki.html = """<table border="1">
                        <tr>
                          <th align="right">Datum</th>
                          <th>9-1-2013</th>
                          <th></th>
                        </tr>
                        <tr id="team_1">
                            <td>Smiley team 1</td>
                            <td>:-)</td>
                            <td>:-)</td>
                        </tr>
                      </table>"""
        self.assertEqual(datetime.datetime.min, self.__wiki.datetime('team_1'))

    def test_date_of_last_measurement(self):
        """ Test the date of the last measurement of the spirit of the team. """
        self.assertEqual(datetime.datetime(2013, 1, 18), self.__wiki.datetime('team_2'))

    def test_invalid_date(self):
        """ Test that an invalid date is taken care of. """
        self.__wiki.html = """<table border="1">
                                <tr>
                                  <th align="right">Datum</th>
                                  <th>9-1--2013</th>
                                </tr>
                                <tr id="team_1">
                                    <td>Smiley team 1</td>
                                    <td>:-)</td>
                                </tr>
                              </table>"""
        self.assertEqual(datetime.datetime.min, self.__wiki.datetime('team_1'))

    def test_line_breaks(self):
        """ Test with line breaks. """
        self.__wiki.html = """<table border="1">
                        <tr>
                          <th align="right">Datum</th>
                          <th>9-1-2013</th>
                          <th>10-1-2014</th>
                        </tr>
                        <tr id="team_1">
                            <td>Smiley team 1</td>
                            <td>:-)<br/></td>
                            <td>:-)<br/></td>
                        </tr>
                      </table>"""
        self.assertEqual(':-)', self.__wiki.team_spirit('team_1'))

    def test_line_breaks_in_dates(self):
        """ Test with line breaks. """
        self.__wiki.html = """<table border="1">
                        <tr>
                          <th align="right">Datum</th>
                          <th>9-1-2013</th>
                          <th>10-1-2014<br/></th>
                        </tr>
                        <tr id="team_1">
                            <td>Smiley team 1</td>
                            <td>:-)<br/></td>
                            <td>:-)<br/></td>
                        </tr>
                      </table>"""
        self.assertEqual(datetime.datetime(2014, 1, 10), self.__wiki.datetime('team_1'))
