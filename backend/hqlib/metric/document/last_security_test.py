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
from ... import metric_source
from ...domain import LowerIsBetterMetric


class LastSecurityTest(LowerIsBetterMetric):
    """ Metric for measuring period from last security test. """

    name = 'Security test'
    unit = 'dag(en)'
    norm_template = 'De securitytest wordt minimaal een keer per {target} {unit} bijgewerkt. Als de test langer ' \
                    'dan {low_target} {unit} geleden is bijgewerkt is deze metriek rood.'
    template = 'Het document "{name}" is {value} {unit} geleden bijgewerkt.'
    missing_template = 'Het document "{name}" is niet aangetroffen.'
    target_value = 180
    low_target_value = 200

    metric_source_class = metric_source.FileWithDate

    def value(self):
        """ Return the number of days since the last security test. """
        if self._metric_source and self._metric_source_id:
            read_date = self._metric_source.get_datetime_from_content(self._metric_source_id)
            if read_date == datetime.datetime.min:
                return -1

            days = (datetime.datetime.now() - read_date).days
            return 0 if days < 0 else days
        else:
            return -1
