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
from __future__ import absolute_import

import datetime
import logging
import re
import time

from hqlib import utils
from hqlib.metric_source import beautifulsoup
from hqlib.metric_source.abstract import team_spirit
from hqlib.metric_source.url_opener import UrlOpener


class Wiki(team_spirit.TeamSpirit, beautifulsoup.BeautifulSoupOpener):
    """ Class representing the Wiki instance. """

    metric_source_name = 'Wiki'

    def __init__(self, wiki_url):
        super(Wiki, self).__init__(url=wiki_url)

    # Team spirit

    @utils.memoized
    def team_spirit(self, team_id):
        """ Return the team spirit of the team. Team spirit is either :-), :-|, or :-( """
        try:
            soup = self.soup(self.url())
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read spirit of team %s", self.url(), team_id)
            return ''
        try:
            row = soup('tr', id=team_id)[0]('td')
        except IndexError:
            logging.warning("Could not find %s in wiki %s", team_id, self.url())
            return ''
        return re.sub(r'[^:\-()|]', '', row[-1].string)

    @utils.memoized
    def date_of_last_team_spirit_measurement(self, team_id):
        """ Return the date that the team spirit of the team was last measured. """
        try:
            soup = self.soup(self.url())
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read date of last spirit measurement of team %s", self.url(), team_id)
            return datetime.datetime.min
        columns = len(soup('tr', id=team_id)[0]('td'))
        date_text = soup('th')[columns - 1].string.strip()
        return self.__parse_date(date_text)

    # Utility methods

    @staticmethod
    def __parse_date(date_text):
        """ Return a parsed version of the date text. """
        year, month, day = time.strptime(date_text, '%d-%m-%Y')[:3]
        return datetime.datetime(year, month, day)
