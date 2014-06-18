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

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils, domain
import datetime
import urllib2


class CoverageReport(domain.MetricSource, beautifulsoup.BeautifulSoupOpener):
    # pylint: disable=abstract-class-not-used
    ''' Abstract class representing a coverage report. '''
    metric_source_name = 'Coverage report'

    def __init__(self, url, username, password):
        super(CoverageReport, self).__init__(url=url, username=username, 
                                             password=password)

    @utils.memoized
    def coverage(self, product):
        ''' Return the ART coverage for a specific product. '''
        coverage_url = self.get_coverage_url(product)
        try:
            soup = self.soup(coverage_url)
        except urllib2.HTTPError:
            coverage = -1
        else:
            coverage = self._parse_coverage_percentage(soup)
        return coverage

    def _parse_coverage_percentage(self, soup):
        ''' Parse the coverage percentage from the soup. '''
        raise NotImplementedError  # pragma: no cover

    @utils.memoized
    def coverage_date(self, product, now=datetime.datetime.now):
        ''' Return the date when the ART coverage for a specific product
            was last successfully measured. '''
        coverage_url = self.get_coverage_date_url(product)
        try:
            soup = self.soup(coverage_url)
        except urllib2.HTTPError:
            coverage_date = now()
        else:
            coverage_date = self._parse_coverage_date(soup)
        return coverage_date

    def _parse_coverage_date(self, soup):
        ''' Parse the coverage date from the soup. '''
        raise NotImplementedError  # pragma: no cover

    def get_coverage_url(self, product):
        ''' Return the url for the coverage report for the product. '''
        return self.url() % product

    def get_coverage_date_url(self, product):
        ''' Return the url for the date when the coverage of the product
            was last measured. '''
        return self.get_coverage_url(product)
