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
import functools
import bs4
from typing import Callable, List

from ..url_opener import UrlOpener
from ... import domain
from hqlib.typing import DateTime


class CoverageReport(domain.MetricSource):
    """ Abstract class representing a coverage report. """
    metric_source_name = 'Coverage report'
    needs_metric_source_id = True

    def __init__(self, url_open: Callable[[str], bytes]=None, **kwargs) -> None:
        self.__url_open = url_open or UrlOpener(**kwargs).url_open
        super().__init__()

    def statement_coverage(self, coverage_url: str) -> int:
        """ Return the ART statement coverage for a specific product. """
        try:
            soup = self.__get_soup(coverage_url)
        except UrlOpener.url_open_exceptions:
            coverage = -1
        else:
            coverage = self._parse_statement_coverage_percentage(soup)
        return coverage

    def _parse_statement_coverage_percentage(self, soup) -> int:
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError  # pragma: no cover

    def branch_coverage(self, coverage_url: str) -> int:
        """ Return the ART branch coverage for a specific product. """
        try:
            soup = self.__get_soup(coverage_url)
        except UrlOpener.url_open_exceptions:
            coverage = -1
        else:
            coverage = self._parse_branch_coverage_percentage(soup)
        return coverage

    def _parse_branch_coverage_percentage(self, soup) -> int:
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError  # pragma: no cover

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *coverage_urls) -> DateTime:
        """ Return the date when the ART coverage for a specific product was last successfully measured. """
        coverage_date_urls = self._get_coverage_date_urls(coverage_urls[0])
        for coverage_date_url in coverage_date_urls:
            try:
                soup = self.__get_soup(coverage_date_url)
            except UrlOpener.url_open_exceptions:
                continue
            else:
                return self._parse_coverage_date(soup)
        return datetime.datetime.min

    def _parse_coverage_date(self, soup) -> DateTime:
        """ Parse the coverage date from the soup. """
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _get_coverage_date_urls(coverage_url: str) -> List[str]:
        """ Return the url for the date when the coverage of the product was last measured. """
        return [coverage_url]

    @functools.lru_cache(maxsize=1024)
    def __get_soup(self, url: str):
        """ Get a beautiful soup of the HTML at the url. """
        return bs4.BeautifulSoup(self.__url_open(url), "lxml")
