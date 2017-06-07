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
import dateutil
import logging
import re
from typing import List, Iterable

from ..abstract import performance_report
from hqlib.typing import DateTime


class ICTULRKPerformanceReport(performance_report.PerformanceReport):
    """ The ICTU LRK performance report is a simple HTML table. """
    COLUMN_90_PERC = 4

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
                cells = row('td')
                if not cells:
                    continue  # Header row
                query_name = cells[0].string
                if not product_query_re.match(query_name):
                    continue  # Not our product
                if len(row('td')) < self.COLUMN_90_PERC + 1:
                    continue  # No color in 90 perc column
                rows.append(row)
        return rows

    def _query_color(self, td) -> bool:
        """ Return whether the query has the specified color. """
        return td['bgcolor']

    def _date_from_soup(self, soup) -> DateTime:
        """ Return the date when performance was last measured. """
        try:
            paragraph = soup('p')[-1]
            date_string = paragraph['data-date']
        except (IndexError, AttributeError) as reason:
            logging.warning("Can't get date from performance report: %s", reason)
            return datetime.datetime.today()
        return dateutil.parser.parse(date_string)

    def urls(self, product: str) -> Iterable[str]:  # pylint: disable=unused-argument
        """ Return the url(s) of the performance report for the specified product and version. """
        return self.__report_urls or [self.url()]


class ICTULRKPerformanceLoadTestReport(ICTULRKPerformanceReport):
    """ An ICTU LRK performance load test. """
    metric_source_name = 'ICTU LRK performanceloadtestrapport'


class ICTULRKPerformanceEnduranceTestReport(ICTULRKPerformanceReport):
    """ An ICTU LRK performance endurance test. """
    metric_source_name = 'ICTU LRK performanceduurtestrapport'


class ICTULRKPerformanceScalabilityTestReport(ICTULRKPerformanceReport):
    """ An ICTU LRK performance scalability test. """
    metric_source_name = 'ICTU LRK performanceschaalbaarheidstestrapport'
