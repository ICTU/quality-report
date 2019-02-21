"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

from typing import List, Tuple
from hqlib import metric_source
from hqlib.typing import MetricValue
from hqlib.domain import LowerIsBetterMetric


class AccessibilityMetric(LowerIsBetterMetric):
    """ Metric for measuring the number of accessibility violations. """

    unit = 'toegankelijkheid violations'
    metric_source_class = metric_source.AxeReport
    name = 'Toegankelijkheid violations'
    target_value = 0
    low_target_value = 0

    extra_info_headers = {"impact": "Impact", "type": "Violation", "page": "Pagina__no-wrap", "element": "Element",
                          "message": "Omschrijving__long_text"}

    def value(self) -> MetricValue:
        """ Return the actual value of the metric. """
        return -1 if not self._metric_source else self._metric_source.nr_violations(self._metric_source_id)

    def extra_info_rows(self) -> List[Tuple[str, str, str, str, str]]:
        return self._metric_source.violations(self._metric_source_id)

    @staticmethod
    def convert_item_to_extra_info(item):
        """ Transforms the item to the extra info format. """
        return (item[0], {"href": item[2], "text": item[1]}, item[3], item[4], item[5])\
            if item else None
