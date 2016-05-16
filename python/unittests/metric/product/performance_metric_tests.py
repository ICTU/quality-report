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

import datetime
import unittest

from qualitylib import metric, domain, metric_source


class FakePerformanceReport(object):
    """ Fake a JMeter performance report. """
    # pylint: disable=unused-argument, invalid-name

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
    def urls(*args):
        """ Return a list of urls for the JMeter reports. """
        return ['http://report1', 'http://report2']

    @staticmethod
    def exists(*args):
        """ Return whether a product exists in the report. """
        return True

    @staticmethod
    def date(*args):
        """ Return the report date. """
        return datetime.datetime.now()


class FakeSubject(object):
    """ Provide for a fake subject. """

    def __init__(self, version='', performance_report_id='performance report id'):
        self.__version = version
        self.__performance_report_id = performance_report_id

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def product_version(self):
        """ Return the version of the subject. """
        return self.__version

    def metric_source_id(self, performance_report):  # pylint: disable=unused-argument
        """ Return the performance report id of the subject. """
        return self.__performance_report_id


class ResponseTimesTestsMixin(object):
    """ Unit tests for the response times metric. """

    expected_queries = -1  # Subclass responsibility
    expected_max_violations = -1  # Subclass responsibility
    expected_wish_violations = -1  # Subclass responsibility
    expected_status = -1  # Subclass responsibility
    expected_report = -1  # Subclass responsibility
    product_version = ''

    def setUp(self):  # pylint: disable=invalid-name
        """ Test fixture. """
        self.__subject = FakeSubject(self.product_version)
        report = FakePerformanceReport(queries=10, queries_violating_max_responsetime=self.expected_max_violations,
                                       queries_violating_wished_responsetime=self.expected_wish_violations)
        self.__project = domain.Project(metric_sources={metric_source.PerformanceReport: report})
        self._metric = metric.ResponseTimes(subject=self.__subject, project=self.__project)

    def test_can_be_measured(self):
        """ Test that the metric can be measured. """
        self.assertTrue(metric.ResponseTimes.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured(self):
        """ Test that the metric can't be measured without performance report. """
        subject = FakeSubject(performance_report_id='')
        self.assertFalse(metric.ResponseTimes.can_be_measured(subject, domain.Project()))

    def test_value(self):
        """ Test that the value of the metric equals None since it is not used. """
        self.assertEqual(None, self._metric.value())

    def test_numerical_value(self):
        """ Test that the numerical value of the metric equals to number of queries that are below the wished and
            maximal response times. """
        self.assertEqual(self.expected_max_violations + self.expected_wish_violations, self._metric.numerical_value())

    def test_status(self):
        """ Test the status of the metric. """
        self.assertEqual(self.expected_status, self._metric.status())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({'Wekelijkse performancemeting (1/2)': 'http://report1',
                          'Wekelijkse performancemeting (2/2)': 'http://report2'},
                         self._metric.url())

    def test_report(self):
        """ Test the report is correct. """
        self.assertTrue(self._metric.report().startswith(self.expected_report))

    def test_missing_performance_report(self):
        """ Test the metric report when the performance report is missing. """

        class MissingPerformanceReport(object):
            # pylint: disable=too-few-public-methods
            """ Fake a missing performance report. """
            @staticmethod
            def exists(*args):  # pylint: disable=unused-argument
                """ Return whether the report exists. """
                return False

            @staticmethod
            def date(*args):  # pylint: disable=unused-argument
                """ Return the date of the report. """
                return datetime.datetime.min

        project = domain.Project(metric_sources={metric_source.PerformanceReport: MissingPerformanceReport()})
        rt_metric = metric.ResponseTimes(subject=FakeSubject(), project=project)
        self.assertTrue(rt_metric.report().startswith('Er is geen performancetestrapport voor'))


class BadResponseTimesTest(ResponseTimesTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the response times metric with bad performance. """

    expected_queries = 10
    expected_max_violations = 4
    expected_wish_violations = 3
    expected_status = 'red'
    product_version = '1.1'
    expected_report = '%d van de %d performancetestqueries draaien niet in 90%% van de gevallen binnen de maximale ' \
        'responsetijd en %d van de %d queries draaien niet in 90%% van de gevallen binnen de gewenste responsetijd ' \
        '(meting ' % (expected_max_violations, expected_queries, expected_wish_violations, expected_queries)


class PerfectReponseTimesTest(ResponseTimesTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the response times metric with perfect response times. """

    expected_queries = 10
    expected_max_violations = 0
    expected_wish_violations = 0
    expected_status = 'perfect'
    expected_report = 'Alle %d performancetestqueries draaien in 90%% van de gevallen binnen de gewenste ' \
                      'responsetijd (meting ' % expected_queries


class OnlyMaxResponseTimesViolated(ResponseTimesTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the response times metric with max response times violated. """

    expected_queries = 10
    expected_max_violations = 4
    expected_wish_violations = 0
    expected_status = 'red'
    expected_report = '%d van de %d performancetestqueries draaien niet in 90%% van de gevallen binnen de maximale ' \
                      'responsetijd (meting ' % (expected_max_violations, expected_queries)


class OnlyWishedResponseTimesViolated(ResponseTimesTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the response times metric with wished response times violated. """

    expected_queries = 10
    expected_max_violations = 0
    expected_wish_violations = 3
    expected_status = 'yellow'
    expected_report = '%d van de %d performancetestqueries draaien niet in 90%% van de gevallen binnen de gewenste ' \
                      'responsetijd (meting ' % (expected_wish_violations, expected_queries)
