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
import logging

from hqlib.typing import MetricValue

from ... import metric_source
from ...domain import LowerIsBetterMetric


class LastSecurityTest(LowerIsBetterMetric):
    """ Metric for measuring period from last security test. """

    name = 'Beveiligingstest frequentie'
    unit = 'dag(en)'
    norm_template = 'De beveiligingstest wordt minimaal een keer per {target} {unit} uitgevoerd. Als de test langer ' \
                    'dan {low_target} {unit} geleden is uitgevoerd is deze metriek rood.'
    template = 'De beveiligingstest is {value} {unit} geleden uitgevoerd.'
    missing_template = 'De datum van de laatste beveiligingstest is niet aangetroffen.'
    target_value = 180
    low_target_value = 360

    metric_source_class = metric_source.FileWithDate

    def value(self) -> MetricValue:
        """ Return the number of days since the last security test. """
        if not (self._metric_source and self._metric_source_id):
            return -1

        read_date = self._metric_source.get_datetime_from_content(self._metric_source_id)
        if read_date == datetime.datetime.min:
            return -1

        if read_date > datetime.datetime.now() + datetime.timedelta(seconds=60):
            logging.warning("%s at %s returned a date and time in the future: %s",
                            self.metric_source_class.metric_source_name, self._metric_source.url(), read_date)
            return -1

        return max(0, (datetime.datetime.now() - read_date).days)
