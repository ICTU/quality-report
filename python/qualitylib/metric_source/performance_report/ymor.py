"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
import re

from .. import beautifulsoup
from ..abstract import performance_report
from ... import utils


class Ymor(performance_report.PerformanceReport, beautifulsoup.BeautifulSoupOpener):
    """ The Ymor performance report is a variant of a JMeter report. """
    metric_source_name = 'Ymor performance report'
    needs_metric_source_id = True
    COLUMN_90_PERC = 5

    def __init__(self, report_url):
        super(Ymor, self).__init__(url=report_url)

    def queries(self, product, version):
        """ Return the number of performance queries. """
        return len(self.__query_rows(product, version))

    def queries_violating_max_responsetime(self, product, version):
        """ Return the number of performance queries that violate the maximum response time. """
        return self.__queries_violating_response_time(product, version, 'red')

    def queries_violating_wished_responsetime(self, product, version):
        """ Return the number of performance queries that violate the maximum response time we'd like to meet. """
        return self.__queries_violating_response_time(product, version, 'yellow')

    def __queries_violating_response_time(self, product, version, color):
        """ Return the number of queries that are violating either the maximum or the desired response time. """
        return len([row for row in self.__query_rows(product, version)
                    if row('td')[self.COLUMN_90_PERC]['class'] == color])

    @utils.memoized
    def __query_rows(self, product, version):
        """ Return the queries for the specified product and version. """
        rows = []
        product_query_re = re.compile(product[0])
        urls = self.urls(product, version)
        for url in urls:
            soup = self.soup(url)
            for row in soup('tr'):
                query_names = row('td', attrs={'class': 'name'})
                if not query_names:
                    continue  # Header row
                query_name = query_names[0].string
                if not product_query_re.match(query_name):
                    continue  # Not our product
                if not row('td')[self.COLUMN_90_PERC].has_key('class'):
                    continue  # No color in 90 perc column
                rows.append(row)
        return rows

    @utils.memoized
    def date(self, product, version):
        """ Return the date when performance was last measured. """
        urls = self.urls(product, version)
        if urls:
            url = list(urls)[0]  # Any url is fine
            soup = self.soup(url)
            try:
                table = soup('table', attrs={'class': 'config'})[0]
                date_string = table('tr')[2]('td')[1].string
            except IndexError:
                logging.warning("Can't get date from performance report %s", url)
                return datetime.datetime.today()
            date_parts = [int(part) for part in date_string.split('.')]
            return datetime.datetime(*date_parts)
        else:
            return datetime.datetime.min

    def exists(self, product, version):
        """ Return whether a performance report exists for the specified product and version. """
        return bool(self.urls(product, version))

    @utils.memoized
    def urls(self, product, version):  # pylint: disable=unused-argument
        """ Return the url(s) of the performance report for the specified product and version. """
        return [self.url()]  # FIXME: Do Ymor reports contain the product and version?
