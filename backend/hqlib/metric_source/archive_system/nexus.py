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
import xml.etree.cElementTree

from hqlib.typing import DateTime
from .. import url_opener
from ..abstract.archive_system import ArchiveSystem


class Nexus(ArchiveSystem):
    """ Class representing a Nexus archive system. """
    metric_source_name = 'Nexus'

    def __init__(self, **kwargs) -> None:
        self.__url_opener = url_opener.UrlOpener(**kwargs)
        super().__init__()

    def last_changed_date(self, path: str) -> DateTime:
        try:
            contents = self.__url_opener.url_read(path)
        except url_opener.UrlOpener.url_open_exceptions:
            return datetime.datetime.min
        root = xml.etree.cElementTree.fromstring(contents)
        most_recent_string = sorted(node.text for node in root.findall('.//lastModified'))[-1]
        return self.__parse_date_time(most_recent_string)

    @staticmethod
    def __parse_date_time(date_time_string: str) -> DateTime:
        """ Parse the date time string and return a datetime instance. """
        date, time = date_time_string.split(' ')[:2]  # Ignore timezone
        year, month, day = date.split('-')
        hms, millisecond = time.split('.')
        hour, minute, second = hms.split(':')
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(millisecond))
