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
import logging
import re
import time

from typing import List

from hqlib.metric_source import beautifulsoup
from hqlib.metric_source.abstract import team_spirit
from hqlib.metric_source.url_opener import UrlOpener
from hqlib.typing import DateTime


class Wiki(team_spirit.TeamSpirit, beautifulsoup.BeautifulSoupOpener):
    """ Class representing the Wiki instance. """

    metric_source_name = 'Wiki'

    def __init__(self, wiki_url: str) -> None:
        super().__init__(url=wiki_url)

    # Metric source API

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:
        """ Return the url(s) to the metric source for the metric source id. """
        return [self.url() + metric_source_id for metric_source_id in metric_source_ids]

    # Team spirit

    def team_spirit(self, team_id: str) -> str:
        """ Return the team spirit of the team. Team spirit is either :-), :-|, or :-( """
        url = self.url() + team_id
        try:
            soup = self.soup(url)
        except UrlOpener.url_open_exceptions as reason:
            logging.warning("Could not open %s to read spirit of team %s: %s", url, team_id, reason)
            return ''
        try:
            last_cell = soup('tr')[1]('td')[-1]
        except IndexError:
            logging.warning("Could not find last spirit for team %s in wiki %s", team_id, url)
            return ''
        try:
            smiley = re.sub(r'[^:\-()|]', '', last_cell.contents[0])
        except (IndexError, TypeError) as reason:
            logging.warning("Could not find a smiley in %s: %s", url, reason)
            return ''
        return smiley if smiley in (":-)", ":-(", ":-|") else ""

    def datetime(self, *team_ids: str) -> DateTime:
        """ Return the date that the team spirit of the team was last measured. """
        url = self.url() + team_ids[0]
        try:
            soup = self.soup(url)
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read date of last spirit measurement of team %s", url, team_ids[0])
            return datetime.datetime.min
        try:
            last_cell = soup('tr')[0]('th')[-1]
            date_text = last_cell.contents[0].strip()
        except (IndexError, AttributeError, TypeError) as reason:
            logging.warning("Could not read the date of the last spirit measurement of team %s from %s: %s",
                            team_ids[0], url, reason)
            return datetime.datetime.min
        try:
            return self.__parse_date(date_text)
        except ValueError as reason:
            logging.warning("Could not parse the date of the last spirit measurement of team %s from %s: %s",
                            team_ids[0], url, reason)
            return datetime.datetime.min

    # Utility methods

    @staticmethod
    def __parse_date(date_text: str) -> DateTime:
        """ Return a parsed version of the date text. """
        year, month, day = time.strptime(date_text, '%d-%m-%Y')[:3]
        return datetime.datetime(year, month, day)
