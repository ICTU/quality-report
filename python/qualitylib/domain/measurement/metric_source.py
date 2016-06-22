"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

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
from __future__ import absolute_import

from ..base import DomainObject


class MetricSource(DomainObject):  # pylint: disable=too-few-public-methods
    """ Base class for metric sources. """
    metric_source_name = ''
    needs_metric_source_id = False
    needs_values_as_list = False

    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = self.metric_source_name or 'Unknown metric source'
        super(MetricSource, self).__init__(*args, **kwargs)


class MissingMetricSource(MetricSource):
    # pylint: disable=too-few-public-methods
    """ Class that represents a missing metric source. """

    def __getattr__(self, attribute):
        return self.__default_method

    @staticmethod
    def __default_method(*args, **kwargs):  # pylint: disable=unused-argument
        """ Do nothing and return nothing for any method called. """
        return

    def __nonzero__(self):
        return False

    def __getitem__(self, index):
        raise StopIteration
