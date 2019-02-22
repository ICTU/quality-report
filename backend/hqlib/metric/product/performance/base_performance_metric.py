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


from typing import List

from hqlib import domain
from hqlib.typing import MetricValue


class PerformanceMetricMixin(domain.Metric):
    """ Base class for performance metrics. """

    def _metric_source_urls(self) -> List[str]:
        """ Return a list of metric source urls. """
        return self._metric_source.urls(self._metric_source_id) if self._metric_source and self._metric_source_id \
            else []

    def value(self) -> MetricValue:
        """ Return the metric value. """
        return super().value()

    def _is_value_better_than(self, target: MetricValue) -> bool:
        """ Return the metric value. """
        return super()._is_value_better_than(target)
