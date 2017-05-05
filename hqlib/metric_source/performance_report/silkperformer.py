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
from typing import List, Iterable

from ..abstract import performance_report
from hqlib.typing import DateTime


class SilkPerformerPerformanceReport(performance_report.PerformanceReport):
    """ The Silk Performer performance report is a variant of a JMeter report. """
    COLUMN_90_PERC = 5

    def __init__(self, *args, **kwargs) -> None:
        self.__report_urls = kwargs.pop('report_urls', None)
        super().__init__(*args, **kwargs)

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        rows = []
        product_query_re = re.compile(product[0])
        urls = self.urls(product)
        for url in urls:
            soup = self.soup(url)
            for row in soup('tr'):
                query_names = row('td', attrs={'class': ['name']})
                if not query_names:
                    continue  # Header row
                query_name = query_names[0].string
                if not product_query_re.match(query_name):
                    continue  # Not our product
                if len(row('td')) < self.COLUMN_90_PERC + 1 or not row('td')[self.COLUMN_90_PERC].has_attr('class'):
                    continue  # No color in 90 perc column
                rows.append(row)
        return rows

    def _date_from_soup(self, soup) -> DateTime:
        """ Return the date when performance was last measured. """
        try:
            table = soup('table', attrs={'class': ['config']})[0]
            date_string = table('tr')[2]('td')[1].string
        except IndexError:
            logging.warning("Can't get date from performance report")
            return datetime.datetime.today()
        year, month, day, hour, minute, second = [int(part) for part in date_string.split('.')][:6]
        return datetime.datetime(year, month, day, hour, minute, second)

    def urls(self, product: str) -> Iterable[str]:  # pylint: disable=unused-argument
        """ Return the url(s) of the performance report for the specified product and version. """
        return self.__report_urls or [self.url()]


class SilkPerformerPerformanceLoadTestReport(SilkPerformerPerformanceReport):
    """ A performance load test done with Silk Performer. """
    metric_source_name = 'Silk Performer performanceloadtestrapport'


class SilkPerformerPerformanceEnduranceTestReport(SilkPerformerPerformanceReport):
    """ A performance endurance test done with Silk Performer. """
    metric_source_name = 'Silk Performer performanceduurtestrapport'


class SilkPerformerPerformanceScalabilityTestReport(SilkPerformerPerformanceReport):
    """ A performance scalability test done with Silk Performer. """
    metric_source_name = 'Silk Performer performanceschaalbaarheidstestrapport'
