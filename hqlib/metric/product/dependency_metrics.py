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

from ..metric_source_mixin import SonarDashboardMetricMixin
from ...domain import LowerIsBetterMetric


class CyclicDependencies(SonarDashboardMetricMixin, LowerIsBetterMetric):
    """ Return the number of cyclic dependencies between packages. """

    name = 'Hoeveelheid cyclische afhankelijkheden'
    unit = 'cyclische afhankelijkheden'
    norm_template = 'Maximaal {target} {unit} tussen packages. Meer dan 10 is rood.'
    template = '{name} heeft {value} {unit}.'
    target_value = 0
    low_target_value = 10

    def value(self):
        cycles = self._metric_source.package_cycles(self._sonar_id())
        return -1 if cycles is None else cycles
