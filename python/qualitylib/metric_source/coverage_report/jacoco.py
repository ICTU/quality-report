'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import


import datetime


from ..abstract import coverage_report
from ... import utils


class JaCoCo(coverage_report.CoverageReport):
    ''' Class representing an JaCoCo coverage report. '''
    metric_source_name = 'JaCoCo coverage report'

    def _get_coverage_date_url(self, coverage_url):
        return coverage_url[:-len('index.html')] + '.sessions.html'

    def _parse_statement_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 1)

    def _parse_branch_coverage_percentage(self, soup):
        return self.__parse_coverage_percentage(soup, 3)

    @staticmethod
    def __parse_coverage_percentage(soup, td_index):
        ''' Return the statement or branch coverage percentage. '''
        coverage_text = soup('tfoot')[0]('td')[td_index].string
        missed, total = (utils.parse_us_int(text) for text in coverage_text.split(' of '))
        if total > 0:
            return round(100 * (total - missed) / float(total))
        else:
            return 0

    def _parse_coverage_date(self, soup):
        coverage_date = datetime.datetime.min
        session_rows = soup('tbody')[0]('tr')
        for row in session_rows:
            session_date_time = utils.parse_us_date_time(row('td')[2].string)
            coverage_date = max(coverage_date, session_date_time)
        return coverage_date
