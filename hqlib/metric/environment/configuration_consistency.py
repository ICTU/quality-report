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

from hqlib import metric_source
from hqlib.domain import LowerIsBetterMetric


class JavaVersionConsistency(LowerIsBetterMetric):
    """ Metric for measuring the number of inconsistencies in an environment. """

    name = 'Javaversie-consistentie'
    unit = 'verschillende Java versies'
    norm_template = 'Er is precies een versie van Java in gebruik. Meer dan {low_target} {unit} is rood.'
    template = 'Er zijn {value} {unit} in gebruik.'
    perfect_value = 1
    target_value = 1
    low_target_value = 2
    metric_source_classes = (metric_source.AnsibleConfigReport,)

    def value(self):
        versions = self._metric_source.java_versions(self._metric_source_id)
        return -1 if versions is None else versions


class JavaVersionConsistencyAge(LowerIsBetterMetric):
    """ Metric for measuring how long ago the version check was run. """
    name = 'Javaversie-consistentie leeftijd'
    unit = 'dagen'
    norm_template = 'De Javaversie-consistentierapportage is maximaal {target} {unit} geleden gemaakt. ' \
                    'Langer dan {low_target} {unit} geleden is rood.'
    perfect_template = 'De Javaversie-consistentierapportage van {name} is vandaag gemaakt.'
    template = 'De Javaversie-consistentierapportage van {name} is {value} {unit} geleden gemaakt.'
    target_value = 3
    low_target_value = 7
    metric_source_classes = (metric_source.AnsibleConfigReport,)

    def value(self):
        return -1 if self._missing() else \
            (datetime.datetime.now() - self._metric_source.datetime(self._metric_source_id)).days

    def _missing(self):
        return self._metric_source.datetime(self._metric_source_id) in (None, datetime.datetime.min)
