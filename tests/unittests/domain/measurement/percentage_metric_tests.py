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

import unittest

from hqlib import domain, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class PercentageMetricUnderTest(domain.HigherPercentageIsBetterMetric):
    """ Implement nominator and denominator for test purposes. """
    # pylint: disable=too-few-public-methods
    def __init__(self, numerator=10, denominator=20, *args, **kwargs):
        self.__numerator = numerator
        self.__denominator = denominator
        super().__init__(*args, **kwargs)

    def _numerator(self):
        return self.__numerator

    def _denominator(self):
        return self.__denominator


class PercentageMixinTest(unittest.TestCase):
    """ Test case for the percentage mixin class. """
    def setUp(self):
        self.__project = domain.Project()

    def test_value(self):
        """ Test that the value of the metric is numerator divided by denominator. """
        metric = PercentageMetricUnderTest(project=self.__project)
        self.assertEqual(50, metric.value())

    def test_denominator_is_zero(self):
        """ Test that the value of the metric is the maximum value when the denominator is zero. """
        metric = PercentageMetricUnderTest(project=self.__project, denominator=0)
        self.assertEqual(100, metric.value())

    def test_missing_numerator(self):
        """ Test that the value of the metric is -1 when the numerator is missing. """
        metric = PercentageMetricUnderTest(project=self.__project, numerator=-1)
        self.assertEqual(-1, metric.value())

    def test_missing_denominator(self):
        """ Test that the value of the metric is -1 when the denominator is missing. """
        metric = PercentageMetricUnderTest(project=self.__project, denominator=-1)
        self.assertEqual(-1, metric.value())

    def test_missing_numerator_and_denominator(self):
        """ Test that the value of the metric is -1 when both numerator and denominator are missing. """
        metric = PercentageMetricUnderTest(project=self.__project, numerator=-1, denominator=-1)
        self.assertEqual(-1, metric.value())


class LowerPercentageIsBetterMetricUnderTest(domain.LowerPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override LowerPercentageIsBetterMetric to implement abstract methods that are needed for running the
        unit tests. """
    low_target_value = 20
    target_value = 10
    numerator = 0
    denominator = 0

    def _numerator(self):
        return self.numerator

    def _denominator(self):
        return self.denominator


class PercentageMetricTestCase(unittest.TestCase):
    """ Test case for percentage metrics. """

    def setUp(self):
        self.__subject = FakeSubject()
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self._metric = self.metric_under_test_class()(self.__subject, project=project)

    @staticmethod
    def metric_under_test_class():
        """ Return the metric class to be tested. """
        raise NotImplementedError  # pragma: no cover

    def set_metric_value(self, numerator, denominator):
        """ Set the metric value by means of the numerator and denominator. """
        # pylint: disable=attribute-defined-outside-init
        self._metric.numerator = numerator
        self._metric.denominator = denominator


class LowerPercentageIsBetterMetricTest(PercentageMetricTestCase):
    """ Test case for the LowerPercentageIsBetterMetric domain class. """

    @staticmethod
    def metric_under_test_class():
        return LowerPercentageIsBetterMetricUnderTest

    def test_perfect_status(self):
        """ Test that the default status is perfect when the score is 100%. """
        self.assertEqual('perfect', self._metric.status())

    def test_green_status(self):
        """ Test that the default status is green when the score is below the low target. """
        self.set_metric_value(1, 100)
        self.assertEqual('green', self._metric.status())

    def test_yellow_status(self):
        """ Test that the  status is yellow when the score is between the low target and target. """
        self.set_metric_value(20, 100)
        self.assertEqual('yellow', self._metric.status())

    def test_red_status(self):
        """ Test that the status is red when the score is higher than the low target. """
        self.set_metric_value(40, 100)
        self.assertEqual('red', self._metric.status())

    def test_y_axis_range(self):
        """ Test that the y axis range is 0-100. """
        self.assertEqual((0, 100), self._metric.y_axis_range())

    def test_default_report(self):
        """ Test that the default report. """
        self.set_metric_value(0, 0)
        self.assertEqual('Subclass responsibility', self._metric.report())


class HigherPercentageIsBetterMetricUnderTest(domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override HigherPercentageIsBetterMetric to implement abstract methods that are needed for running the
        unit tests. """
    low_target_value = 80
    target_value = 90
    numerator = 0
    denominator = 0

    def _numerator(self):
        return self.numerator

    def _denominator(self):
        return self.denominator


class HigherPercentageIsBetterMetricTest(PercentageMetricTestCase):
    """ Test case for the HigherPercentageIsBetterMetric domain class. """

    @staticmethod
    def metric_under_test_class():
        return HigherPercentageIsBetterMetricUnderTest

    def test_red_status(self):
        """ Test that the status is red when the percentage is lower than the low target. """
        self.set_metric_value(0, 5)
        self.assertEqual('red', self._metric.status())

    def test_yellow_status(self):
        """ Test that the status is yellow when the percentage is lower than the target. """
        self.set_metric_value(85, 100)
        self.assertEqual('yellow', self._metric.status())

    def test_green_status(self):
        """ Test that the status is green when the metric value is higher than the target value. """
        self.set_metric_value(95, 100)
        self.assertEqual('green', self._metric.status())

    def test_perfect_status(self):
        """ Test that the status is perfect when the metric value is 100%. """
        self.set_metric_value(234, 234)
        self.assertEqual('perfect', self._metric.status())

    def test_y_axis_range(self):
        """ Test that the y axis range is 0-100. """
        self.assertEqual((0, 100), self._metric.y_axis_range())

    def test_default_report(self):
        """ Test that the default report. """
        self.set_metric_value(0, 5)
        self.assertEqual('Subclass responsibility', self._metric.report())
