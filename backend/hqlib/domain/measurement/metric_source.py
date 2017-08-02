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

from typing import Any, Callable, List

from ..base import DomainObject
from hqlib.typing import DateTime


class MetricSource(DomainObject):  # pylint: disable=too-few-public-methods
    """ Base class for metric sources. """
    metric_source_name: str = ''
    needs_metric_source_id: bool = False
    needs_values_as_list: bool = False

    def __init__(self, *args: str, **kwargs: str) -> None:
        if 'name' not in kwargs:
            kwargs['name'] = self.metric_source_name or 'Unknown metric source'
        super().__init__(*args, **kwargs)

    def metric_source_urls(self, *metric_source_ids: str) -> List[str]:  # pylint: disable=no-self-use
        """ Return the url(s) to the metric source for the metric source id. """
        return list(metric_source_ids)  # Default implementation assumes the metric source ids are urls.

    def datetime(self, *metric_source_ids: str) -> DateTime:  # pylint: disable=unused-argument,no-self-use
        """ Return the date and time of the last measurement. """
        return datetime.datetime.now()


class MissingMetricSource(MetricSource):
    """ Class that represents a missing metric source. """

    def url(self) -> str:
        return ''

    def datetime(self, *metric_source_ids: str) -> DateTime:  # pylint: disable=unused-argument,no-self-use
        return datetime.datetime.min

    def __getattr__(self, attribute: str) -> Callable[..., None]:
        return self.__default_method

    @staticmethod
    def __default_method(*args: Any, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """ Do nothing and return nothing for any method called. """
        return

    def __bool__(self) -> bool:
        return False

    def __getitem__(self, index: int) -> None:
        raise StopIteration
