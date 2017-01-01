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

from ..abstract import coverage_report
from ... import utils


class JaCoCo(coverage_report.CoverageReport):
    """ Class representing an JaCoCo coverage report. """
    metric_source_name = 'JaCoCo coverage rapport'

    @staticmethod
    def _get_coverage_date_url(coverage_url):
        return coverage_url[:-len('index.html')] + '.sessions.html'

    def _parse_statement_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 1)

    def _parse_branch_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 3)

    @staticmethod
    def __parse_coverage_percentage(soup, td_index):
        """ Return the statement or branch coverage percentage. """
        try:
            coverage_text = soup('tfoot')[0]('td')[td_index].string
        except IndexError:
            logging.error("Can't parse %s", soup)
            raise
        coverage_text = coverage_text.replace(',', '').replace('.', '')
        missed, total = (int(text) for text in coverage_text.split(' of '))
        return round(100 * (total - missed) / float(total)) if total > 0 else 0

    def _parse_coverage_date(self, soup):
        coverage_date = datetime.datetime.min
        session_rows = soup('tbody')[0]('tr')
        for row in session_rows:
            date_time_string = row('td')[2].string
            try:
                session_date_time = utils.parse_us_date_time(date_time_string)
            except ValueError:
                session_date_time = self.__parse_non_us_date_time(date_time_string)
            coverage_date = max(coverage_date, session_date_time)
        return coverage_date

    @staticmethod
    def __parse_non_us_date_time(date_time_string):
        date_string, time_string = date_time_string.split(' ')
        day_string, month_string, year_string = date_string.split('-')
        hour_string, minute_string, second_string = time_string.split(':')
        year, month, day = int(year_string), utils.ABBREVIATED_MONTHS[month_string], int(day_string)
        hour, minute, second = int(hour_string), int(minute_string), int(second_string)
        return datetime.datetime(year, month, day, hour, minute, second)
