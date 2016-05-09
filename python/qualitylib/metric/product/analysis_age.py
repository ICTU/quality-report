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

from ..metric_source_mixin import SonarDashboardMetricMixin
from ..quality_attributes import CODE_QUALITY
from ...domain import LowerIsBetterMetric


class SonarAnalysisAge(SonarDashboardMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    """ Metric to measure the age of the latest Sonar analysis. """

    name = 'Leeftijd meest recente Sonar analyse'
    norm_template = 'De meest recente Sonar analyse is maximaal {target} dagen oud. ' \
                    'Meer dan {low_target} dagen is rood.'
    template = 'De meest recente Sonar analyse van {name} is {value} dagen oud.'
    target_value = 6 * 7
    low_target_value = 9 * 7
    quality_attribute = CODE_QUALITY

    def value(self):
        now = datetime.datetime.now()
        latest_analysis_datetime = self._sonar.analysis_datetime(self._sonar_id())
        if latest_analysis_datetime == datetime.datetime.min:
            return -1
        age = now - latest_analysis_datetime
        return age.days
