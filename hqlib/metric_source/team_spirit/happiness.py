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
import time

from hqlib import utils
from hqlib.metric_source.abstract import team_spirit
from hqlib.metric_source.url_opener import UrlOpener


class Happiness(team_spirit.TeamSpirit):
    """ Class representing the ICTU Happiness instance. """

    metric_source_name = 'Happiness'

    def __init__(self, url, url_open=None):
        self.__url_open = url_open or UrlOpener().url_open
        super(Happiness, self).__init__(url=url)

    # Team spirit

    @utils.memoized
    def team_spirit(self, team_id):
        """ Return the team spirit of the team. Team spirit is either :-), :-|, or :-( """
        try:
            json = utils.eval_json(self.__url_open(self.__api_url()).read())
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read spirit of team %s", self.__api_url(), team_id)
            return ''
        try:
            return {'1': ':-(', '2': ':-(', '3': ':-|', '4': ':-)', '5': ':-)'}[json[-1]['smiley']]
        except (KeyError, IndexError) as reason:
            logging.warning("Could not find smiley for %s in %s: %s", team_id, self.__api_url(), reason)
            return ''

    @utils.memoized
    def date_of_last_team_spirit_measurement(self, team_id):
        """ Return the date that the team spirit of the team was last measured. """
        try:
            json = utils.eval_json(self.__url_open(self.__api_url()).read())
        except UrlOpener.url_open_exceptions:
            logging.warning("Could not open %s to read date of least spirit measurement of team %s", self.__api_url(),
                            team_id)
            return datetime.datetime.min
        try:
            return self.__parse_date(json[-1]['datum'])
        except (KeyError, IndexError) as reason:
            logging.warning("Could not find smiley for %s in %s: %s", team_id, self.__api_url(), reason)
            return datetime.datetime.min

    # Utility methods

    def __api_url(self):
        """ Return the api url. """
        url = self.url()
        if not url.endswith('/'):
            url += '/'
        return url + 'api/'

    @staticmethod
    def __parse_date(date_text):
        """ Return a parsed version of the date text. """
        year, month, day = time.strptime(date_text, '%Y-%m-%d')[:3]
        return datetime.datetime(year, month, day)
