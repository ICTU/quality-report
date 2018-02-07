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
from typing import List

from hqlib.typing import DateTime
from .html_coverage_report import HTMLCoverageReport
from ... import utils


class JaCoCo(HTMLCoverageReport):
    """ Class representing an JaCoCo coverage report. """
    metric_source_name = 'JaCoCo coverage rapport'

    @staticmethod
    def _get_coverage_date_urls(coverage_url: str) -> List[str]:
        base_url = coverage_url[:-len('index.html')]
        return [base_url + 'jacoco-sessions.html', base_url + '.sessions.html']

    def _parse_statement_coverage_percentage(self, soup) -> float:
        return self.__parse_coverage_percentage(soup, 1)

    def _parse_branch_coverage_percentage(self, soup) -> float:
        return self.__parse_coverage_percentage(soup, 3)

    @staticmethod
    def __parse_coverage_percentage(soup, td_index: int) -> float:
        """ Return the statement or branch coverage percentage. """
        try:
            coverage_text = soup('tfoot')[0]('td')[td_index].string
        except IndexError:
            logging.error("Can't parse %s", soup)
            raise
        coverage_text = coverage_text.replace(',', '').replace('.', '')
        missed, total = (int(text) for text in coverage_text.split(' of '))
        return 100 * (total - missed) / float(total) if total > 0 else 0

    def _parse_coverage_date(self, soup) -> DateTime:
        coverage_date = datetime.datetime.min
        try:
            session_rows = soup('tbody')[0]('tr')
        except IndexError:
            logging.error("Can't find JaCoCo session table in %s", soup)
            return coverage_date
        for row in session_rows:
            date_time_string = row('td')[2].string
            try:
                session_date_time = utils.parse_us_date_time(date_time_string)
            except ValueError:
                session_date_time = self.__parse_non_us_date_time(date_time_string)
            coverage_date = max(coverage_date, session_date_time)
        return coverage_date

    @staticmethod
    def __parse_non_us_date_time(date_time_string: str) -> DateTime:
        """ Parse the date and time string. """
        date, time = date_time_string.split(' ')
        day, month, year = date.split('-')
        hour, minute, second = time.split(':')
        return datetime.datetime(int(year), utils.ABBREVIATED_MONTHS[month], int(day),
                                 int(hour), int(minute), int(second))
