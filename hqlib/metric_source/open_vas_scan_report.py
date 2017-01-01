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

import bs4

from . import url_opener
from .. import domain


class OpenVASScanReport(domain.MetricSource):
    """ Class representing open VAS Scan reports. """
    metric_source_name = 'Open VAS Scan rapport'
    needs_metric_source_id = True

    def __init__(self, url_open=None, **kwargs):
        self._url_open = url_open or url_opener.UrlOpener(**kwargs).url_open
        super(OpenVASScanReport, self).__init__()

    def alerts(self, risk_level, *report_urls):
        """ Return the number of alerts of the specified risk level. """
        assert risk_level in ('low', 'medium', 'high')
        nr_alerts = 0
        for url in report_urls:
            try:
                soup = bs4.BeautifulSoup(self._url_open(url), "html.parser")
            except url_opener.UrlOpener.url_open_exceptions:
                return -1
            else:
                nr_alerts += self.__parse_alerts(soup, risk_level)
        return nr_alerts

    @staticmethod
    def __parse_alerts(soup, risk_level):
        """ Get the number of alerts from the HTML soup. """
        summary_table = soup('table')[0]('table')[1]  # The whole report is one big table with nested tables.
        column = dict(high=3, medium=4, low=5)[risk_level]
        return int(summary_table('tr')[-1]('td')[column].string)
