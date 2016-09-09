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

from ... import domain, metric_source


class PerformanceMetric(domain.LowerIsBetterMetric):
    """ Base class for performance metrics. """
    unit = 'performancetestqueries'
    target_value = 0
    level = 'Subclass responsibility'
    norm_template = 'Het product heeft geen {unit} die de {level} overschrijden. ' \
                    'Meer dan {low_target} {unit} die de {level} overschrijden is rood.'
    template = '{value} van de {total} {unit} van {name} overschrijden de {level}.'
    metric_source_classes = (metric_source.PerformanceReport,)

    @classmethod
    def norm_template_default_values(cls):
        values = super(PerformanceMetric, cls).norm_template_default_values()
        values['level'] = cls.level
        return values

    def value(self):
        return self._violating_queries() if self._metric_source and self._metric_source_id else -1

    def _violating_queries(self):
        """ Return the number of queries not meting the required response times. """
        raise NotImplementedError  # pragma: no cover

    def __total_queries(self):
        """ Return the total number of queries. """
        return self._metric_source.queries(*self._product_id()) if self._metric_source and self._metric_source_id \
            else -1

    def _metric_source_urls(self):
        return self._metric_source.urls(*self._product_id()) or []

    def _parameters(self):
        parameters = super(PerformanceMetric, self)._parameters()
        parameters.update(dict(level=self.level, total=self.__total_queries()))
        return parameters

    def _product_id(self):
        """ Return the performance report id and version of the product. """
        return self._metric_source_id, self._subject.product_version()


class PerformanceTestWarnings(PerformanceMetric):
    """ Performance test warnings metric. """
    name = 'Hoeveelheid performance test warnings'
    level = 'gewenste responsetijd'
    low_target_value = 5

    def _violating_queries(self):
        return self._metric_source.queries_violating_wished_responsetime(*self._product_id())


class PerformanceTestErrors(PerformanceMetric):
    """ Performance test errors metric. """
    name = 'Hoeveelheid performance test errors'
    level = 'maximale responstijd'
    low_target_value = 0

    def _violating_queries(self):
        return self._metric_source.queries_violating_max_responsetime(*self._product_id())
