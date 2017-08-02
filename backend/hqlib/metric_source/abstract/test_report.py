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
from typing import Callable

from .. import url_opener
from ... import domain
from ...typing import DateTime


class TestReport(domain.MetricSource):
    """ Abstract class representing a test report. """
    metric_source_name = 'Test report'
    needs_metric_source_id = True

    def __init__(self, url_read: Callable[[str], str]=None, **kwargs) -> None:
        self._url_read = url_read or url_opener.UrlOpener(**kwargs).url_read
        super().__init__()

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *report_urls: str) -> DateTime:
        """ Return the (oldest) date and time of the reports. """
        return min([self._report_datetime(report_url) for report_url in report_urls]) if report_urls else \
            datetime.datetime.min

    @functools.lru_cache(maxsize=1024)
    def passed_tests(self, *report_urls: str) -> int:
        """ Return the number of passed tests. """
        return sum([self._passed_tests(report_url) for report_url in report_urls]) if report_urls else -1

    @functools.lru_cache(maxsize=1024)
    def failed_tests(self, *report_urls: str) -> int:
        """ Return the number of failed tests. """
        return sum([self._failed_tests(report_url) for report_url in report_urls]) if report_urls else -1

    @functools.lru_cache(maxsize=1024)
    def skipped_tests(self, *report_urls: str) -> int:
        """ Return the number of skipped tests. """
        return sum([self._skipped_tests(report_url) for report_url in report_urls]) if report_urls else -1

    def _report_datetime(self, report_url: str) -> DateTime:
        """ Return the date and time of the report. """
        raise NotImplementedError  # pragma: nocover

    def _passed_tests(self, report_url: str) -> int:
        """ Return the number of passed tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover

    def _failed_tests(self, report_url: str) -> int:
        """ Return the number of failed tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover

    def _skipped_tests(self, report_url: str) -> int:
        """ Return the number of skipped tests as reported by the test report. """
        raise NotImplementedError  # pragma: nocover
