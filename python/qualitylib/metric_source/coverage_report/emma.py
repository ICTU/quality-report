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
import time

from ..abstract import coverage_report


class Emma(coverage_report.CoverageReport):
    ''' Class representing an Emma coverage report. '''
    metric_source_name = 'Emma coverage report'

    def _parse_coverage_percentage(self, soup):
        coverage_text = soup('td')[5].string
        return int(coverage_text.split('%')[0])

    def _parse_coverage_date(self, soup):
        header = soup('th', 'tl')[0].contents[1]
        # The Emma report contains non-breaking spaces (&nbsp;) in the
        # header instead of normal spaces (!). Fix it.
        header = header.replace(u'\xa0', ' ')
        datetime_text = header.split('(')[1][len('generated '):-1]
        return self.__parse_datetime(datetime_text)

    @staticmethod
    def __parse_datetime(datetime_text):
        ''' Parse and return the date/time. '''
        try:
            parsed_datetime = time.strptime(datetime_text,
                                            '%a %b %d %H:%M:%S %Z %Y')
        except ValueError:
            _, month, day, time_text, _, year = datetime_text.split(' ')
            hour, minute, second = time_text.split(':')
            month = dict(jan=1, feb=2, mrt=3, mar=3, apr=4, mei=5, may=5,
                         jun=6, jul=7, aug=8, sep=9, okt=10, oct=10,
                         nov=11, dec=12)[month[:3].lower()]
            parsed_datetime = (int(year), month, int(day),
                               int(hour), int(minute), int(second))
        return datetime.datetime(*(parsed_datetime[0:6]))
