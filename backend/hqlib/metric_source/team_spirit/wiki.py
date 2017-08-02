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
import logging
import re
import time

from hqlib.metric_source import beautifulsoup
from hqlib.metric_source.abstract import team_spirit
from hqlib.metric_source.url_opener import UrlOpener
from hqlib.typing import DateTime


class Wiki(team_spirit.TeamSpirit, beautifulsoup.BeautifulSoupOpener):
    """ Class representing the Wiki instance. """

    metric_source_name = 'Wiki'

    def __init__(self, wiki_url: str) -> None:
        super().__init__(url=wiki_url)

    # Team spirit

    def team_spirit(self, team_id: str) -> str:
        """ Return the team spirit of the team. Team spirit is either :-), :-|, or :-( """
        try:
            soup = self.soup(self.url())
        except UrlOpener.url_open_exceptions as reason:
            logging.warning("Could not open %s to read spirit of team %s: %s", self.url(), team_id, reason)
            return ''
        try:
            row = soup('tr', id=team_id)[0]('td')
        except IndexError:
            logging.warning("Could not find %s in wiki %s", team_id, self.url())
            return ''
        try:
            return re.sub(r'[^:\-()|]', '', row[-1].contents[0])
        except TypeError as reason:
            logging.warning("Could not find a string in the last row: %s", reason)
            return ''

    def datetime(self, *team_ids: str) -> DateTime:
        """ Return the date that the team spirit of the team was last measured. """
        try:
            soup = self.soup(self.url())
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read date of last spirit measurement of team %s", self.url(),
                            team_ids[0])
            return datetime.datetime.min
        columns = len(soup('tr', id=team_ids[0])[0]('td'))
        try:
            date_text = soup('th')[columns - 1].contents[0].strip()
        except (IndexError, AttributeError) as reason:
            logging.error("Could not read the date of the last spirit measurement of team %s from %s: %s",
                          team_ids[0], self.url(), reason)
            return datetime.datetime.min
        try:
            return self.__parse_date(date_text)
        except ValueError as reason:
            logging.error("Could not parse the date of the last spirit measurement of team %s from %s: %s",
                          team_ids[0], self.url(), reason)
            return datetime.datetime.min

    # Utility methods

    @staticmethod
    def __parse_date(date_text: str) -> DateTime:
        """ Return a parsed version of the date text. """
        year, month, day = time.strptime(date_text, '%d-%m-%Y')[:3]
        return datetime.datetime(year, month, day)
