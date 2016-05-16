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

import datetime

from qualitylib import metric_source
from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.quality_attributes import ENVIRONMENT_QUALITY


class JavaVersionConsistency(LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric for measuring the number of inconsistencies in an environment. """

    name = 'Java versie consistentie'
    norm_template = 'Er is precies een versie van Java in gebruik. Meer dan {low_target} versies is rood. ' \
        'De rapportage is maximaal {old_age} oud. Meer dan {max_old_age} oud is rood.'
    template = 'Er zijn {value} verschillende versies van Java in gebruik.'
    perfect_value = 1
    target_value = 1
    low_target_value = 2
    old_age = datetime.timedelta(days=3)
    max_old_age = datetime.timedelta(days=7)
    quality_attribute = ENVIRONMENT_QUALITY
    metric_source_classes = (metric_source.AnsibleConfigReport,)

    def __init__(self, *args, **kwargs):
        super(JavaVersionConsistency, self).__init__(*args, **kwargs)
        self.__report = self._project.metric_source(metric_source.AnsibleConfigReport)
        self.__report_url = self._subject.metric_source_id(self.__report)

    def value(self):
        return self.__report.java_versions(self.__report_url)

    def url(self):
        return {'Ansible configuration report': self.__report_url}

    def _date(self):
        """ Return the last measurement date. """
        return self.__report.date(self.__report_url)
