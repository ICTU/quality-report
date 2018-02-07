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

import functools
from typing import Callable

from hqlib.typing import DateTime
from ..url_opener import UrlOpener
from ... import domain


class CoverageReport(domain.MetricSource):
    """ Abstract class representing a coverage report. """
    metric_source_name = 'Coverage report'

    def __init__(self, url_open: Callable[[str], bytes] = None, **kwargs) -> None:
        self.__url_open = url_open or UrlOpener(**kwargs).url_open
        super().__init__()

    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        raise NotImplementedError

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date when the coverage for a specific product was last successfully measured. """
        raise NotImplementedError


class UnittestCoverageReport(CoverageReport):
    """ Abstract class representing a unit test coverage report. """
    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        raise NotImplementedError

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date when the coverage for a specific product was last successfully measured. """
        raise NotImplementedError


class ARTCoverageReport(CoverageReport):
    """ Abstract class representing a unit test coverage report. """
    def statement_coverage(self, metric_source_id: str) -> float:
        """ Return the statement coverage for a specific product. """
        raise NotImplementedError

    def branch_coverage(self, metric_source_id: str) -> float:
        """ Return the branch coverage for a specific product. """
        raise NotImplementedError

    @functools.lru_cache(maxsize=1024)
    def datetime(self, *metric_source_ids: str) -> DateTime:
        """ Return the date when the coverage for a specific product was last successfully measured. """
        raise NotImplementedError
