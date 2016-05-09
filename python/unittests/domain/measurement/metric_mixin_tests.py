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

import unittest

from qualitylib import domain, metric_source
from unittests.domain.measurement.fake import FakeHistory, FakeSubject


class DummyMetric(domain.Metric):
    # pylint: disable=too-few-public-methods
    """ Override to implement abstract methods that are needed for running the unit tests. """
    def value(self):
        """ Return a dummy value. """
        return 0


class MetaMetricUnderTest(domain.MetaMetricMixin, domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Use MetaMetricMixin to create a concrete meta metric that can be tested. """
    pass


class MetaMetricMixinTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test case for meta metric mixin class. """

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        subject = [DummyMetric(FakeSubject(), project=project)]
        self.__metric = MetaMetricUnderTest(subject, project=project)

    def test_value(self):
        """ Test the value of the metric. """
        self.assertEqual(0, self.__metric.value())


class PercentageMetricUnderTest(domain.HigherPercentageIsBetterMetric):
    """ Implement nominator and denominator for test purposes. """
    # pylint: disable=too-few-public-methods
    def __init__(self, numerator=10, denominator=20, *args, **kwargs):
        self.__numerator = numerator
        self.__denominator = denominator
        super(PercentageMetricUnderTest, self).__init__(*args, **kwargs)

    def _numerator(self):
        return self.__numerator

    def _denominator(self):
        return self.__denominator


class PercentageMixinTest(unittest.TestCase):
    """ Test case for the percentage mixin class. """
    def setUp(self):  # pylint: disable=invalid-name
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
