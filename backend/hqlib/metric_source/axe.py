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

import csv
import re
import logging
import functools
from typing import List
from io import StringIO
from .. import domain
from ..metric_source import url_opener


class AxeReport(domain.MetricSource):
    """ Class representing the aXe report instance. """

    metric_source_name = 'Axe report'

    def __init__(self, **kwargs) -> None:
        self._url_read = url_opener.UrlOpener(**kwargs).url_read
        super().__init__()

    def nr_violations(self, url: str) -> int:
        """ Return the number of user stories. """
        try:
            return len(self._get_csv_dict(url))
        except url_opener.UrlOpener.url_open_exceptions:
            logging.error("Error retrieving accessibility report from %s.", url)
            return -1

    @functools.lru_cache(maxsize=8192)
    def _get_csv_dict(self, url) -> List:
        return [(row['Impact'], row['Violation Type'], row['Help'], re.sub(r'http[s]?://[^/]+', '', row['URL']),
                 row['DOM Element'], row['Messages'])
                for row in csv.DictReader(StringIO(self._url_read(url), newline=None))]

    def violations(self, url: str) -> List:
        """ Return the list of fields violations """
        try:
            return self._get_csv_dict(url)
        except url_opener.UrlOpener.url_open_exceptions:
            logging.error("Error retrieving accessibility report from %s.", url)
            return []
