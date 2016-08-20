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

from ..metric_source_mixin import SonarDashboardMetricMixin
from ... import metric_source
from ...domain import LowerIsBetterMetric
from ...formatting import HTMLFormatter


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


class SnapshotDependencies(LowerIsBetterMetric):
    """ Metric for measuring the number of the dependencies on snapshot versions of other products. """
    name = 'Hoeveelheid snapshot afhankelijkheden'
    unit = 'afhankelijkheden'
    norm_template = 'Maximaal {target} {unit} op snapshot versies van andere producten. Meer dan {low_target} is rood.'
    template = '{name} heeft {value} {unit} op snapshot versies van andere producten.'
    target_value = 0
    low_target_value = 2
    metric_source_classes = (metric_source.VersionControlSystem, metric_source.Pom)

    @classmethod
    def is_applicable(cls, product):
        # Only report for released versions:
        return super(SnapshotDependencies, cls).is_applicable(product) and product.product_version()

    def __init__(self, *args, **kwargs):
        self.__report = kwargs.pop('report')
        super(SnapshotDependencies, self).__init__(*args, **kwargs)

    def value(self):
        return len(self.__snapshot_dependencies())

    def url(self):
        urls = dict()
        for dependency in self.__snapshot_dependencies():
            product = self.__report.get_product(*dependency)
            label = '{}:{}'.format(dependency[0], dependency[1] or 'trunk')
            urls[label] = HTMLFormatter.product_url(product)
        return urls

    def __snapshot_dependencies(self):
        """ Return a list of snapshot dependencies of this product. """
        return [dependency for dependency in self._subject.dependencies() if not dependency[1]]

