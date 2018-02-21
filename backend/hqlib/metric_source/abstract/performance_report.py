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
from typing import List, Iterable

from hqlib.typing import DateTime, TimeDelta
from ..url_opener import UrlOpener
from ... import domain


class PerformanceReport(domain.MetricSource):
    """ Abstract class representing a performance report. """
    metric_source_name = 'Performancerapport'

    def __init__(self, report_url: str, *args, **kwargs) -> None:
        super().__init__(url=report_url, *args, **kwargs)

    def urls(self, product: str) -> Iterable[str]:
        """ Return the report urls for the specified product. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def queries(self, product: str) -> int:
        """ Return the number of performance queries. """
        try:
            return len(self._query_rows(product))
        except UrlOpener.url_open_exceptions:
            return -1
        except ValueError:
            return -1

    @functools.lru_cache(maxsize=1024)
    def queries_violating_max_responsetime(self, product: str) -> int:
        """ Return the number of performance queries that violate the maximum response time. """
        try:
            return self.__queries_violating_response_time(product, 'red')
        except UrlOpener.url_open_exceptions:
            return -1
        except ValueError:
            return -1

    @functools.lru_cache(maxsize=1024)
    def queries_violating_wished_responsetime(self, product: str) -> int:
        """ Return the number of performance queries that violate the maximum response time we'd like to meet. """
        try:
            return self.__queries_violating_response_time(product, 'yellow')
        except UrlOpener.url_open_exceptions:
            return -1
        except ValueError:
            return -1

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *products: str) -> DateTime:
        """ Return the date when performance was last measured. """
        urls = self.urls(products[0])
        if urls:
            url = list(urls)[0]  # Any url is fine
            return self._datetime_from_url(url)
        return datetime.datetime.min

    def duration(self, product: str) -> TimeDelta:
        """ Return the duration of the performance test. """
        urls = self.urls(product)
        if urls:
            url = list(urls)[0]  # Any url is fine
            return self._duration_from_url(url)
        return datetime.timedelta.max

    def _datetime_from_url(self, url: str) -> DateTime:
        """ Return the date when the performance was last measured. """
        raise NotImplementedError

    def _duration_from_url(self, url: str) -> TimeDelta:
        """ Return the duration of the performance test. """
        raise NotImplementedError

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        raise NotImplementedError

    def __queries_violating_response_time(self, product: str, color: str) -> int:
        """ Return the number of queries that are violating either the maximum or the desired response time. """
        return len([row for row in self._query_rows(product) if self._has_query_color(row, color)])

    def _has_query_color(self, row, color: str) -> bool:
        """ Return whether the row has a query with the specified color. """
        raise NotImplementedError


class PerformanceLoadTestReport(PerformanceReport):
    """ Performance load test report. """
    def urls(self, product: str) -> Iterable[str]:
        """ Return the report urls for the specified product. """
        raise NotImplementedError

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        raise NotImplementedError

    def _datetime_from_url(self, url: str) -> DateTime:
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError

    def _duration_from_url(self, url: str) -> TimeDelta:
        """ Return the duration of the performance test. """
        raise NotImplementedError

    def _has_query_color(self, row, color: str) -> bool:
        """ Return whether the row has a query has the specified color. """
        raise NotImplementedError


class PerformanceEnduranceTestReport(PerformanceReport):
    """ Performance endurance test report. """
    def urls(self, product: str) -> Iterable[str]:
        """ Return the report urls for the specified product. """
        raise NotImplementedError

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        raise NotImplementedError

    def _datetime_from_url(self, url: str) -> DateTime:
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError

    def _duration_from_url(self, url: str) -> TimeDelta:
        """ Return the duration of the performance test. """
        raise NotImplementedError

    def _has_query_color(self, row, color: str) -> bool:
        """ Return whether the row has a query has the specified color. """
        raise NotImplementedError


class PerformanceScalabilityTestReport(PerformanceReport):
    """ Performance scalability test report. """
    def urls(self, product: str) -> Iterable[str]:
        """ Return the report urls for the specified product. """
        raise NotImplementedError

    def _query_rows(self, product: str) -> List:
        """ Return the queries for the specified product. """
        raise NotImplementedError

    def _datetime_from_url(self, url: str) -> DateTime:
        """ Return the date when the performance was last measured based on the report at the url. """
        raise NotImplementedError

    def _duration_from_url(self, url: str) -> TimeDelta:
        """ Return the duration of the performance test. """
        raise NotImplementedError

    def _has_query_color(self, row, color: str) -> bool:
        """ Return whether the row has a query has the specified color. """
        raise NotImplementedError
