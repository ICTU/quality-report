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

import unittest

from hqlib import domain, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class LowerIsBetterMetricUnderTest(domain.LowerIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override LowerIsBetterMetric to implement abstract methods that are needed for running the unit tests. """
    low_target_value = target_value = 1

    def __init__(self, *args, **kwargs):
        self.__value = kwargs.pop('value', 0)
        super().__init__(*args, **kwargs)

    def value(self):
        """ Return the measured value. """
        return self.__value


class LowerIsBetterMetricTest(unittest.TestCase):
    """ Test case for the LowerIsBetterMetric domain class. """

    def setUp(self):
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.History: FakeHistory()})

    def test_default_status(self):
        """ Test that the default status is perfect. """
        metric = LowerIsBetterMetricUnderTest(self.__subject, project=self.__project)
        self.assertEqual('perfect', metric.status())

    def test_impossible_value(self):
        """ Test that the status is missing if the value is below zero. """
        metric = LowerIsBetterMetricUnderTest(self.__subject, project=self.__project, value=-1)
        self.assertEqual('missing', metric.status())


class HigherIsBetterMetricUnderTest(domain.HigherIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Override HigherIsBetterMetric to implement abstract methods that are needed for running the unit tests. """
    low_target_value = target_value = 100

    @staticmethod
    def value():
        """ Return the measured value. """
        return 0


class HigherIsBetterMetricTest(unittest.TestCase):
    """ Test case for the HigherIsBetterMetric domain class. """

    def setUp(self):
        self.__subject = FakeSubject()
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        self.__metric = HigherIsBetterMetricUnderTest(self.__subject, project=project)

    def test_default_status(self):
        """ Test that the default status is red. """
        self.assertEqual('red', self.__metric.status())

    def test_technical_debt(self):
        """ Test that the status is grey when the current value is accepted technical debt. """
        # pylint: disable=attribute-defined-outside-init
        self.__subject.technical_debt_target = lambda metric: domain.TechnicalDebtTarget(0, 'Comment')
        self.assertEqual('grey', self.__metric.status())
