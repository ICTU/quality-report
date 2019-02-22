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

import datetime
import unittest

from typing import Type

from hqlib import metric, metric_source, domain
from hqlib.metric import PerformanceLoadTestAge


class FakePerformanceReport:
    """ Fake a JMeter performance report. """
    # pylint: disable=too-few-public-methods

    metric_source_name = 'Performancerapport'

    @staticmethod
    def duration(*args):  # pylint: disable=unused-argument
        """ Return the duration of the performance test. """
        return datetime.timedelta(minutes=90, seconds=4)


class FakeSubject:
    """ Provide for a fake subject. """

    def __init__(self, performance_report_id='performance report id'):
        self.__performance_report_id = performance_report_id

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, performance_report):  # pylint: disable=unused-argument
        """ Return the performance report id of the subject. """
        return self.__performance_report_id


class PerformanceLoadTestDurationTest(unittest.TestCase):
    """ Unit tests for the performance load test duration metric. """
    metric_class: Type[PerformanceLoadTestAge] = metric.PerformanceLoadTestDuration
    metric_source_class = metric_source.ICTUPerformanceLoadTestReport
    test_type = 'performanceloadtest'

    def setUp(self):
        self.__subject = FakeSubject()
        self.__report = FakePerformanceReport()
        self.__project = domain.Project(metric_sources={self.metric_class.metric_source_class: self.__report})
        self.__metric = self.metric_class(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the value reported by the performance report. """
        self.assertEqual(90, self.__metric.value())

    def test_value_when_not_configured(self):
        """ Test that the value of the metric is -1 when the report hasn't been configured. """
        performance_metric = self.metric_class(subject=FakeSubject(), project=domain.Project())
        self.assertEqual(-1, performance_metric.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """

        class MissingPerformanceReport:  # pylint: disable=too-few-public-methods
            """ Fake a missing performance report. """

            @staticmethod
            def duration(*args):  # pylint: disable=unused-argument
                """ Return a default value. """
                return datetime.timedelta.max

        project = domain.Project(metric_sources={
            self.metric_class.metric_source_class: MissingPerformanceReport()})
        performance_metric = self.metric_class(subject=FakeSubject(), project=project)
        self.assertEqual(-1, performance_metric.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        self.assertEqual("De uitvoeringstijd van de {type} van FakeSubject is 90 minuten.".format(type=self.test_type),
                         self.__metric.report())

    def test_is_applicable(self):
        """ Test that the metric is applicable if the metric source can deliver the required information. """
        self.assertFalse(self.__metric.is_applicable())
        report = self.metric_source_class(report_url="http://report")
        project = domain.Project(metric_sources={self.metric_class.metric_source_class: report})
        performance_metric = self.metric_class(self.__subject, project)
        self.assertTrue(performance_metric.is_applicable())


class PerformanceEnduranceTestDuration(PerformanceLoadTestDurationTest):
    """ Unit tests for the performance endurance test duration metric. """
    metric_class = metric.PerformanceEnduranceTestDuration
    metric_source_class = metric_source.ICTUPerformanceEnduranceTestReport
    test_type = 'performanceduurtest'


class PerformanceScalabilityTestDuration(PerformanceLoadTestDurationTest):
    """ Unit tests for the performance scalability test duration metric. """
    metric_class = metric.PerformanceScalabilityTestDuration
    metric_source_class = metric_source.ICTUPerformanceScalabilityTestReport
    test_type = 'performanceschaalbaarheidstest'
