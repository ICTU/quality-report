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

import unittest
from unittest.mock import MagicMock
from hqlib import domain, metric_source
from hqlib.metric.product.accessibility_metrics import AccessibilityMetric


class AccessibilityViolationsTest(unittest.TestCase):
    """ Unit tests for the AccessibilityViolations class metric. """

    def test_accessibility_metric_properties(self):
        """ Test the properties. """
        project = domain.Project()
        project.metric_sources = MagicMock(return_value=[None])

        metric = AccessibilityMetric(subject=MagicMock(), project=project)

        self.assertEqual('toegankelijkheid violations', metric.unit)
        self.assertEqual(metric.metric_source_class, metric_source.AxeReport)
        self.assertEqual('Toegankelijkheid violations', metric.name)
        self.assertEqual(0, metric.target_value)
        self.assertEqual(0, metric.low_target_value)

    def test_value(self):
        """ Test the value of number of alerts. """
        metric_source_object = MagicMock()
        metric_source_object.nr_violations = MagicMock(return_value=42)
        project = domain.Project(metric_sources={metric_source_object.AxeReport: metric_source_object})
        project.metric_sources = MagicMock(return_value=[metric_source_object])
        metric = AccessibilityMetric(subject=MagicMock(), project=project)

        self.assertEqual(42, metric.value())
        metric_source_object.nr_violations.assert_called_once()

    def test_value_no_metric_source(self):
        """ Test the value of number of alerts when there is no metric source. """
        metric_source_object = None
        project = domain.Project()
        project.metric_sources = MagicMock(return_value=[metric_source_object])
        metric = AccessibilityMetric(subject=MagicMock(), project=project)

        self.assertEqual(-1, metric.value())

    def test_convert_item_to_extra_info(self):
        """ Test the value extra_info is converted as expected. """

        self.assertEqual((0, {"href": 2, "text": 1}, 3, 4, 5),
                         AccessibilityMetric.convert_item_to_extra_info([0, 1, 2, 3, 4, 5]))

    def test_convert_item_to_extra_info_none(self):
        """ Test the None value is returned as extra_info if the item was empty. """

        self.assertEqual(None, AccessibilityMetric.convert_item_to_extra_info([]))
