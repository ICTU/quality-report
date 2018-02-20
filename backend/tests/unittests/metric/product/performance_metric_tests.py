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
import unittest

from typing import Type

from hqlib import metric, metric_source, domain
from hqlib.metric.product.performance_metrics import PerformanceTestAge, PerformanceMetric


class FakePerformanceReport(object):
    """ Fake a JMeter performance report. """
    # pylint: disable=unused-argument, invalid-name

    metric_source_name = 'Performancerapport'

    def __init__(self, queries=0, queries_violating_max_responsetime=0, queries_violating_wished_responsetime=0):
        self.__queries = queries
        self.__queries_violating_max_responsetime = queries_violating_max_responsetime
        self.__queries_violating_wished_responsetime = queries_violating_wished_responsetime

    def queries(self, *args):
        """ Return the number of queries for the product. """
        return self.__queries

    def queries_violating_max_responsetime(self, *args):
        """ Return the number of queries that violate the maximum response times. """
        return self.__queries_violating_max_responsetime

    def queries_violating_wished_responsetime(self, *args):
        """ Return the number of queries that violate the wished response times . """
        return self.__queries_violating_wished_responsetime

    @staticmethod
    def datetime(*args):
        """ Return the date and time of the report. """
        return datetime.datetime(2017, 1, 1)

    @staticmethod
    def duration(*args):
        """ Return the duration of the performance test. """
        return datetime.timedelta(minutes=90, seconds=4)


class FakeSubject(object):
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


class PerformanceLoadTestWarningsTest(unittest.TestCase):
    """ Unit tests for the performance load test warnings metric. """
    metric_class: Type[PerformanceMetric] = metric.PerformanceLoadTestWarnings
    expected_violations = 4
    expected_status = 'yellow'

    def setUp(self):
        self.__subject = FakeSubject()
        self.__report = FakePerformanceReport(queries=10, queries_violating_max_responsetime=self.expected_violations,
                                              queries_violating_wished_responsetime=self.expected_violations)
        self.__project = domain.Project(metric_sources={self.metric_class.metric_source_class: self.__report})
        self.__metric = self.metric_class(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value is correcrt. """
        self.assertEqual(self.expected_violations, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('4 van de 10 {0} van FakeSubject overschrijden de {1}.'.
                         format(self.metric_class.unit, self.metric_class.level), self.__metric.report())

    def test_status(self):
        """ Test the status of the metric. """
        self.assertEqual(self.expected_status, self.__metric.status())

    def test_missing_performance_report(self):
        """ Test the metric report when the performance report is missing. """

        class MissingPerformanceReport(object):  # pylint: disable=too-few-public-methods
            """ Fake a missing performance report. """

            @staticmethod
            def queries_violating_max_responsetime(*args):  # pylint: disable=unused-argument
                """ Return a default value. """
                return -1

            queries = queries_violating_wished_responsetime = queries_violating_max_responsetime

        project = domain.Project(metric_sources={
            self.metric_class.metric_source_class: MissingPerformanceReport()})
        performance_metric = self.metric_class(subject=FakeSubject(), project=project)
        self.assertTrue(performance_metric.report().endswith('kon niet gemeten worden omdat niet alle benodigde '
                                                             'bronnen beschikbaar zijn.'))

    def test_norm_default_values(self):
        """ Test that the norm template can be printed. """
        self.assertEqual('Het product heeft geen {0} die de {1} overschrijden. Meer dan {2} {0} die de {1} '
                         'overschrijden is rood.'.format(self.metric_class.unit, self.metric_class.level,
                                                         self.metric_class.low_target_value),
                         self.metric_class.norm_template.format(**self.metric_class.norm_template_default_values()))


class PerformanceLoadTestErrorsTest(PerformanceLoadTestWarningsTest):
    """ Unit tests for the performance load test errors metric. """
    metric_class = metric.PerformanceLoadTestErrors
    expected_status = 'red'


class PerformanceEnduranceTestWarningsTest(PerformanceLoadTestWarningsTest):
    """ Unit tests for the performance endurance test warnings metrics. """
    metric_class = metric.PerformanceEnduranceTestWarnings
    expected_status = 'yellow'


class PerformanceEnduranceTestErrorsTest(PerformanceLoadTestWarningsTest):
    """ Unit tests for the performance endurance test errors metrics. """
    metric_class = metric.PerformanceEnduranceTestErrors
    expected_status = 'red'


class PerformanceScalabilityTestWarningsTest(PerformanceLoadTestWarningsTest):
    """ Unit tests for the performance scalability test warnings metrics. """
    metric_class = metric.PerformanceScalabilityTestWarnings
    expected_status = 'yellow'


class PerformanceScalabilityTestErrorsTest(PerformanceLoadTestWarningsTest):
    """ Unit tests for the performance scalability test errors metrics. """
    metric_class = metric.PerformanceScalabilityTestErrors
    expected_status = 'red'


class PerformanceLoadTestAgeTest(unittest.TestCase):
    """ Unit tests for the performance load test age metric. """
    metric_class: Type[PerformanceTestAge] = metric.PerformanceLoadTestAge
    test_type = 'performanceloadtest'

    def setUp(self):
        self.__subject = FakeSubject()
        self.__report = FakePerformanceReport(queries=10)
        self.__project = domain.Project(metric_sources={self.metric_class.metric_source_class: self.__report})
        self.__metric = self.metric_class(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the report date as reported by Jenkins. """
        expected = (datetime.datetime.now() - self.__report.datetime('id')).days
        self.assertEqual(expected, self.__metric.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """

        class MissingPerformanceReport(object):  # pylint: disable=too-few-public-methods
            """ Fake a missing performance report. """

            @staticmethod
            def datetime(*args):  # pylint: disable=unused-argument
                """ Return a default value. """
                return datetime.datetime.min

        project = domain.Project(metric_sources={
            self.metric_class.metric_source_class: MissingPerformanceReport()})
        performance_metric = self.metric_class(subject=FakeSubject(), project=project)
        self.assertEqual(-1, performance_metric.value())

    def test_report(self):
        """ Test that the report for the metric is correct. """
        days = (datetime.datetime.now() - self.__report.datetime()).days
        self.assertEqual('De {0} van FakeSubject is {1} dagen geleden gedraaid.'.format(self.test_type, days),
                         self.__metric.report())


class PerformanceEnduranceTestAge(PerformanceLoadTestAgeTest):
    """ Unit tests for the performance endurance test age metric. """
    metric_class = metric.PerformanceEnduranceTestAge
    test_type = 'performanceduurtest'


class PerformanceScalabilityTestAge(PerformanceLoadTestAgeTest):
    """ Unit tests for the performance scalability test age metric. """
    metric_class = metric.PerformanceScalabilityTestAge
    test_type = 'performanceschaalbaarheidstest'


class PerformanceLoadTestDurationTest(unittest.TestCase):
    """ Unit tests for the performance load test duration metric. """
    metric_class: Type[PerformanceTestAge] = metric.PerformanceLoadTestDuration
    metric_source_class = metric_source.SilkPerformerPerformanceLoadTestReport
    test_type = 'performanceloadtest'

    def setUp(self):
        self.__subject = FakeSubject()
        self.__report = FakePerformanceReport(queries=10)
        self.__project = domain.Project(metric_sources={self.metric_class.metric_source_class: self.__report})
        self.__metric = self.metric_class(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that value of the metric equals the report date as reported by Jenkins. """
        self.assertEqual(90, self.__metric.value())

    def test_value_when_not_configured(self):
        """ Test that the value of the metric is -1 when the report hasn't been configured. """
        performance_metric = self.metric_class(subject=FakeSubject(), project=domain.Project())
        self.assertEqual(-1, performance_metric.value())

    def test_value_when_missing(self):
        """ Test that the value is negative when the test report is missing. """

        class MissingPerformanceReport(object):  # pylint: disable=too-few-public-methods
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
    metric_source_class = metric_source.SilkPerformerPerformanceEnduranceTestReport
    test_type = 'performanceduurtest'


class PerformanceScalabilityTestDuration(PerformanceLoadTestDurationTest):
    """ Unit tests for the performance scalability test duration metric. """
    metric_class = metric.PerformanceScalabilityTestDuration
    metric_source_class = metric_source.SilkPerformerPerformanceScalabilityTestReport
    test_type = 'performanceschaalbaarheidstest'
