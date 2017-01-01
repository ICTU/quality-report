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

from ... import domain, metric_source


class PerformanceMetric(domain.LowerIsBetterMetric):
    """ Base class for performance metrics. """
    target_value = 0
    level = unit = 'Subclass responsibility'
    norm_template = 'Het product heeft geen {unit} die de {level} overschrijden. ' \
                    'Meer dan {low_target} {unit} die de {level} overschrijden is rood.'
    template = '{value} van de {total} {unit} van {name} overschrijden de {level}.'

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
        return self._metric_source.queries(self._metric_source_id) if self._metric_source and self._metric_source_id \
            else -1

    def _metric_source_urls(self):
        return self._metric_source.urls(self._metric_source_id) if self._metric_source and self._metric_source_id \
            else []

    def _parameters(self):
        parameters = super(PerformanceMetric, self)._parameters()
        parameters.update(dict(level=self.level, total=self.__total_queries()))
        return parameters


# We have different types of performance test metrics, organized along two dimensions: test type and severity.
# The test types are load test, endurance test, and scalability test. The severities are warnings and errors.
# The warnings metrics count the number of performance test cases that take longer than the desired response
# times and the error metrics count the number of performance test cases that take longer than the maximum
# response times. The limits for warning and error are determined by the test reports.


class PerformanceLoadTestMetric(PerformanceMetric):
    """ Base class for performance load test metrics. """
    unit = 'performanceloadtestgevallen'
    metric_source_classes = (metric_source.PerformanceLoadTestReport,)

    def _violating_queries(self):
        """ Return the number of queries not meting the required response times. """
        raise NotImplementedError  # pragma: no cover


class PerformanceLoadTestWarnings(PerformanceLoadTestMetric):
    """ Performance load test warnings metric. """
    name = 'Hoeveelheid performanceloadtestwaarschuwingen'
    level = 'gewenste responsetijd'
    low_target_value = 5

    def _violating_queries(self):
        return self._metric_source.queries_violating_wished_responsetime(self._metric_source_id)


class PerformanceLoadTestErrors(PerformanceLoadTestMetric):
    """ Performance load test errors metric. """
    name = 'Hoeveelheid performanceloadtestoverschrijdingen'
    level = 'maximale responstijd'
    low_target_value = 0

    def _violating_queries(self):
        return self._metric_source.queries_violating_max_responsetime(self._metric_source_id)


class PerformanceEnduranceTestMetric(PerformanceMetric):
    """ Base class for performance endurance test metrics. """
    unit = 'performanceduurtestgevallen'
    metric_source_classes = (metric_source.PerformanceEnduranceTestReport,)

    def _violating_queries(self):
        """ Return the number of queries not meting the required response times. """
        raise NotImplementedError  # pragma: no cover


class PerformanceEnduranceTestWarnings(PerformanceEnduranceTestMetric):
    """ Performance endurance test warnings metric. """
    name = 'Hoeveelheid performanceduurtestwaarschuwingen'
    level = 'gewenste responsetijd'
    low_target_value = 5

    def _violating_queries(self):
        return self._metric_source.queries_violating_wished_responsetime(self._metric_source_id)


class PerformanceEnduranceTestErrors(PerformanceEnduranceTestMetric):
    """ Performance endurance test errors metric. """
    name = 'Hoeveelheid performanceduurtestoverschrijdingen'
    level = 'maximale responstijd'
    low_target_value = 0

    def _violating_queries(self):
        return self._metric_source.queries_violating_max_responsetime(self._metric_source_id)


class PerformanceScalabilityTestMetric(PerformanceMetric):
    """ Base class for performance scalability test metrics. """
    unit = 'performanceschaalbaarheidstestgevallen'
    metric_source_classes = (metric_source.PerformanceScalabilityTestReport,)

    def _violating_queries(self):
        """ Return the number of queries not meting the required response times. """
        raise NotImplementedError  # pragma: no cover


class PerformanceScalabilityTestWarnings(PerformanceScalabilityTestMetric):
    """ Performance scalability test warnings metric. """
    name = 'Hoeveelheid performanceschaalbaarheidstestwaarschuwingen'
    level = 'gewenste responsetijd'
    low_target_value = 5

    def _violating_queries(self):
        return self._metric_source.queries_violating_wished_responsetime(self._metric_source_id)


class PerformanceScalabilityTestErrors(PerformanceScalabilityTestMetric):
    """ Performance scalability test errors metric. """
    name = 'Hoeveelheid performanceschaalbaarheidstestoverschrijdingen'
    level = 'maximale responstijd'
    low_target_value = 0

    def _violating_queries(self):
        return self._metric_source.queries_violating_max_responsetime(self._metric_source_id)
