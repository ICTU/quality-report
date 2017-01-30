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
from __future__ import absolute_import

import datetime

from . import directed_metric


class MetricSourceAgeMetric(directed_metric.LowerIsBetterMetric):
    """ Metric for measuring the age of a metric source. """
    unit = 'dagen'
    target_value = 3
    low_target_value = 7

    def value(self):
        return -1 if self._missing() else \
            (datetime.datetime.now() - self._metric_source.datetime(*self._get_metric_source_ids())).days

    def _missing(self):
        if not self._metric_source:
            return True
        metric_source_ids = self._get_metric_source_ids()
        if self._metric_source.needs_metric_source_id and not metric_source_ids:
            return True
        else:
            return self._metric_source.datetime(*metric_source_ids) in (None, datetime.datetime.min)
