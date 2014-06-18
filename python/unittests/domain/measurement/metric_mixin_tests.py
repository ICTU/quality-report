'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import domain, metric_source
from unittests.domain.measurement.fake import FakeHistory, FakeSubject
import unittest


class DummyMetric(domain.Metric):
    # pylint: disable=too-many-public-methods,W0223
    ''' Override to implement abstract methods that are needed for running 
        the unit tests. '''
    def value(self):
        return 0


class MetaMetricUnderTest(domain.MetaMetricMixin, 
                          domain.HigherPercentageIsBetterMetric):
    # pylint: disable=too-few-public-methods
    ''' Use MetaMetricMixin to create a concrete meta metric that can be 
        tested. '''
    pass


class MetaMetricMixinTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Test case for meta metric mixin class. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.History: FakeHistory()})
        subject = [DummyMetric(FakeSubject(), project=project)]
        self._metric = MetaMetricUnderTest(subject, project=project)

    def test_value(self):
        ''' Test the value of the metric. '''
        self.assertEqual(0, self._metric.value())
