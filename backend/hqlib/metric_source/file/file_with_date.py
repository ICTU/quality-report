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
import json
import logging

import dateutil.parser

from hqlib import domain
from hqlib.typing import DateTime
from .. import url_opener


class FileWithDate(domain.MetricSource):
    """ Class representing a file with a date in ISO format. """
    metric_source_name = 'FileWithDate'

    def __init__(self, **kwargs) -> None:
        self._url_read = url_opener.UrlOpener(**kwargs).url_read
        super().__init__()

    def get_datetime_from_content(self, url: str) -> DateTime:
        """ The content expected is just an ISO string date or simple json with only ISO string date """
        try:
            file_content = self._url_read(url)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        try:
            return dateutil.parser.parse(file_content)
        except ValueError:
            try:
                return dateutil.parser.parse(list(json.loads(file_content).values())[0])
            except (ValueError, AttributeError, IndexError) as reason:
                logging.error("Couldn't parse date and time from %s at %s: %s", self.metric_source_name, url, reason)
        return datetime.datetime.min
