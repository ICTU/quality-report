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

from hqlib.domain.measurement.measurable import MeasurableObject
from hqlib.domain import TechnicalDebtTarget


class MeasurableObjectTests(unittest.TestCase):
    """ Unit tests for the measurable object. """
    def setUp(self):
        self.__metric_options = dict(comment='metric options', target=100, low_target=50,
                                     debt_target=TechnicalDebtTarget(100, 'explanation'))
        self.__measurable = MeasurableObject(
            metric_sources={''.__class__: 'metric_source'},
            metric_source_ids={self.__class__: 'id'},
            metric_options={self.__class__: self.__metric_options})

    def test_no_target(self):
        """ Test that there is no target for an unknown class. """
        self.assertFalse(self.__measurable.target(''.__class__))

    def test_target(self):
        """ Test the target for a known class. """
        self.assertEqual(100, self.__measurable.target(self.__class__))

    def test_no_low_target(self):
        """ Test that there is no low target for an unknown class. """
        self.assertFalse(self.__measurable.low_target(''.__class__))

    def test_low_target(self):
        """ Test the low target for a known class. """
        self.assertEqual(50, self.__measurable.low_target(self.__class__))

    def test_no_technical_debt(self):
        """ Test that there is no technical debt for an unknown class. """
        self.assertFalse(self.__measurable.technical_debt_target(''.__class__))

    def test_technical_debt(self):
        """ Test the technical debt for a known class. """
        target = self.__measurable.technical_debt_target(self.__class__)
        self.assertEqual(100, target.target_value())

    def test_no_metric_source_id(self):
        """ Test the metric source id for an unknown class. """
        self.assertFalse(self.__measurable.metric_source_id(''.__class__))

    def test_metric_source_id(self):
        """ Test the metric source id for a known class. """
        self.assertEqual('id', self.__measurable.metric_source_id(self.__class__))

    def test_no_metric_option(self):
        """ Test the metric option for an unknown class. """
        self.assertFalse(self.__measurable.metric_options(''.__class__))

    def test_metric_options(self):
        """ Test the metric options for a known class. """
        self.assertEqual(self.__metric_options, self.__measurable.metric_options(self.__class__))

    def test_metrics_with_options(self):
        """ Test that the metrics with options can be retrieved. """
        self.assertEqual({self.__class__}, self.__measurable.metrics_with_options())

    def test_unknown_metric_source(self):
        """ Test that the measurable returns None for an unknown metric source class. """
        self.assertFalse(self.__measurable.metric_sources(self.__class__))

    def test_known_metric_source(self):
        """ Test that the measurable returns the instance of a known metric source class. """
        self.assertEqual(['metric_source'], self.__measurable.metric_sources(''.__class__))

    def test_metric_source_classes(self):
        """ Test that the measurable returns a list of all metric source classes. """
        self.assertEqual([''.__class__], self.__measurable.metric_source_classes())

    def test_default_metric_source_classes(self):
        """ Test that the project returns a list of all metric source classes. """
        self.assertEqual([], MeasurableObject().metric_source_classes())
