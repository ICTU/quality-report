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

from hqlib import domain, metric, metric_source
from tests.unittests.domain.measurement.fake import FakeHistory, FakeSubject


class MetaMetricUnderTest(metric.meta_metrics.MetaMetricMixin, domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    """ Use MetaMetricMixin to create a concrete meta metric that can be tested. """
    pass


class MetaMetricMixinTest(unittest.TestCase):
    """ Test case for meta metric mixin class. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.History: FakeHistory()})
        subject = [metric.CriticalViolations(FakeSubject(), project=project)]
        self.__metric = MetaMetricUnderTest(subject, project=project)

    def test_value(self):
        """ Test the value of the metric. """
        self.assertEqual(0, self.__metric.value())
