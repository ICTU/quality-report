'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils, domain
import datetime
import logging
import time


class Wiki(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Wiki instance. '''

    metric_source_name = 'Wiki'

    def __init__(self, wiki_url):
        super(Wiki, self).__init__(url=wiki_url)

    # Team spirit

    @utils.memoized
    def team_spirit(self, team):
        ''' Return the team spirit of the team. Team spirit is either :-), :-|,
            or :-( '''
        soup = self.soup(self.url())
        try:
            row = soup('tr', id='smiley_%s' % team.id_string())[0]('td')
        except IndexError:
            logging.error("Could not find %s in wiki", team.id_string())
            raise
        latest_smiley = row[-1].string
        return latest_smiley.strip() if latest_smiley else ''

    @utils.memoized
    def date_of_last_team_spirit_measurement(self, team):
        ''' Return the date that the team spirit of the team was last
            measured. '''
        soup = self.soup(self.url())
        columns = len(soup('tr', id='smiley_%s' % team.id_string())[0]('td'))
        date_text = soup('th')[columns - 1].string.strip()
        return self.__parse_date(date_text)

    # Comment

    @utils.memoized
    def comment(self, metric_id):
        ''' Return a comment on a metric from the Wiki. '''
        soup = self.soup(self.url())
        try:
            metric_row = soup('table')[1]('tr', id=metric_id)[0]
            return metric_row('td')[1].string.strip()
        except IndexError:
            return ''

    def comment_url(self):
        ''' Return the url for comments. '''
        return self.url()

    # Utility methods

    @staticmethod
    def __parse_date(date_text):
        ''' Return a parsed version of the date text. '''
        year, month, day = time.strptime(date_text, '%d-%m-%Y')[:3]
        return datetime.datetime(year, month, day)
