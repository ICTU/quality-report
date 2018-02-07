"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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
from typing import Callable, List

import bs4

from hqlib.typing import DateTime
from ..abstract.coverage_report import CoverageReport
from ..url_opener import UrlOpener


class HTMLCoverageReport(CoverageReport):
    """ Abstract class representing a HTML coverage report. """

    def __init__(self, url_open: Callable[[str], bytes] = None, **kwargs) -> None:
        self.__url_open = url_open or UrlOpener(**kwargs).url_open
        super().__init__()

    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        try:
            soup = self.__get_soup(metric_source_id)
        except UrlOpener.url_open_exceptions:
            coverage = -1
        else:
            coverage = self._parse_statement_coverage_percentage(soup)
        return coverage

    def _parse_statement_coverage_percentage(self, soup) -> float:
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        try:
            soup = self.__get_soup(metric_source_id)
        except UrlOpener.url_open_exceptions:
            coverage = -1
        else:
            coverage = self._parse_branch_coverage_percentage(soup)
        return coverage

    def _parse_branch_coverage_percentage(self, soup) -> float:
        """ Parse the coverage percentage from the soup. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date when the coverage for a specific product was last successfully measured. """
        coverage_date_urls = self._get_coverage_date_urls(metric_source_ids[0])
        for index, coverage_date_url in enumerate(coverage_date_urls):
            is_last_url = index + 1 == len(coverage_date_urls)
            try:
                soup = self.__get_soup(coverage_date_url, log_error=is_last_url)
            except UrlOpener.url_open_exceptions:
                continue
            return self._parse_coverage_date(soup)
        return datetime.datetime.min

    def _parse_coverage_date(self, soup) -> DateTime:
        """ Parse the coverage date from the soup. """
        raise NotImplementedError

    @staticmethod
    def _get_coverage_date_urls(coverage_url: str) -> List[str]:
        """ Return the url for the date when the coverage of the product was last measured. """
        return [coverage_url]

    @functools.lru_cache(maxsize=1024)
    def __get_soup(self, url: str, log_error: bool = True):
        """ Get a beautiful soup of the HTML at the url. """
        return bs4.BeautifulSoup(self.__url_open(url, log_error=log_error), "lxml")
