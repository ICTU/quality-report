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
from typing import List, Dict, Set, Iterable, Tuple

from .. import url_opener
from ..abstract import performance_report
from ... import utils
from hqlib.typing import DateTime


class JMeterPerformanceReport(performance_report.PerformanceReport):
    """ Class representing the JMeter performance report. """

    metric_source_name = 'Jmeter performance report'
    COLUMN_90_PERC = 10

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        rows = []
        product_query_re = re.compile(product[0])
        urls = self.urls(product)
        for url in urls:
            soup = self.soup(url)
            for row in soup('tr'):
                query_names = row('td', attrs={'class': 'name'})
                if not query_names:
                    continue  # Header row
                query_name = query_names[0].string
                if not product_query_re.match(query_name):
                    continue  # Not our product
                if not row('td')[self.COLUMN_90_PERC].has_attr('class'):
                    continue  # No color in 90 perc column
                rows.append(row)
        return rows

    def _date_from_soup(self, soup) -> DateTime:
        """ Return the date when performance was last measured. """
        try:
            date_text = soup('h2')[0].string.split(' End: ')[1]
        except IndexError:
            logging.warning("Can't get date from performance report")
            return datetime.datetime.today()
        return self.__parse_date(date_text)

    def urls(self, product: str) -> Iterable[str]:
        """ Return the url(s) of the performance report for the specified product. """
        urls: Dict[int, Set[str]] = {0: set()}  # {test_run_number: set(of urls)}
        for filename, url in self.__report_urls():
            urls.setdefault(self.__test_run_number(filename), set()).add(url)
        return urls[max(urls.keys())]  # Return the latest test run

    def __report_urls(self) -> List[Tuple[str, str]]:
        """ Return the url(s) for the performance reports in the report folder. """
        base_url = self.url()
        try:
            soup = self.soup(base_url)
        except url_opener.UrlOpener.url_open_exceptions as reason:
            logging.warning("Couldn't open %s to read report urls: %s", base_url, reason)
            return []
        urls = []
        for list_item in soup('li'):
            filename = list_item('a')[0].string
            if filename.endswith('.html'):
                urls.append((filename, base_url + filename))
        return urls

    @staticmethod
    def __test_run_number(filename: str) -> int:
        """ Return the test run number as contained in the filename. """
        return int(re.search('[0-9]+', filename).group(0))

    @staticmethod
    def __parse_date(date_text: str) -> DateTime:
        """ Return a parsed version of the date text. """
        return utils.parse_uk_date_time_year_last(date_text)


class JMeterPerformanceLoadTestReport(JMeterPerformanceReport):
    """ A performance load test done with JMeter. """
    metric_source_name = 'JMeter performanceloadtestrapport'


class JMeterPerformanceEnduranceTestReport(JMeterPerformanceReport):
    """ A performance endurance test done with JMeter. """
    metric_source_name = 'JMeter performanceduurtestrapport'


class JMeterPerformanceScalabilityTestReport(JMeterPerformanceReport):
    """ A performance scalability test done with JMeter. """
    metric_source_name = 'JMeter performanceschaalbaarheidstestrapport'
