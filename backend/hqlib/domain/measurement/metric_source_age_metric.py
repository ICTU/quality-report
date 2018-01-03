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

from . import directed_metric


class MetricSourceAgeMetric(directed_metric.LowerIsBetterMetric):
    """ Metric for measuring the age of a metric source. """
    unit = 'dagen'
    target_value = 3
    low_target_value = 7

    @functools.lru_cache(maxsize=1024)
    def value(self):
        if self._missing():
            return -1

        days = (datetime.datetime.now() - self._metric_source.datetime(*self._get_metric_source_ids())).days
        return 0 if days < 0 else days

    @functools.lru_cache(maxsize=1024)
    def _missing(self):
        if not self._metric_source:
            return True
        metric_source_ids = self._get_metric_source_ids()
        return self._metric_source.datetime(*metric_source_ids) in (None, datetime.datetime.min)
