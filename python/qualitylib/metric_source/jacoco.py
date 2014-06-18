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

from qualitylib.metric_source import coverage_report
from qualitylib import utils
import datetime


class JaCoCo(coverage_report.CoverageReport):
    ''' Class representing an JaCoCo coverage report. '''
    metric_source_name = 'JaCoCo coverage report'

    def get_coverage_date_url(self, product):
        url = super(JaCoCo, self).get_coverage_date_url(product)
        return url[:-len('index.html')] + '.sessions.html'

    def _parse_coverage_percentage(self, soup):
        instructions_text = soup('tfoot')[0]('td')[1].string
        missed_instructions, total_instructions = (utils.parse_us_int(text) \
            for text in instructions_text.split(' of '))
        if total_instructions > 0:
            return round(100 * (total_instructions - missed_instructions) / 
                         float(total_instructions))
        else:
            return 0

    def _parse_coverage_date(self, soup):
        coverage_date = datetime.datetime.min
        session_rows = soup('tbody')[0]('tr')
        for row in session_rows:
            session_date_time = utils.parse_us_date_time(row('td')[2].string)
            coverage_date = max(coverage_date, session_date_time)
        return coverage_date
