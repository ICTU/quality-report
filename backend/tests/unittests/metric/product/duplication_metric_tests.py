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

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """

    metric_source_name = metric_source.Sonar.metric_source_name

    @staticmethod
    def duplicated_lines(*args):  # pylint: disable=unused-argument
        """ Return the number of duplicated lines. """
        return 15

    @staticmethod
    def lines(*args):  # pylint: disable=unused-argument
        """ Return the number of lines. """
        return 150


class DuplicationTest(unittest.TestCase):
    """ Unit tests for the duplication metric. """

    def setUp(self):
        sonar = FakeSonar()
        project = domain.Project(metric_sources={metric_source.Sonar: sonar})
        product = domain.Product(short_name='PR', name='FakeSubject', metric_source_ids={sonar: 'sonar id'})
        self._metric = metric.JavaDuplication(subject=product, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the percentage of duplicated lines. """
        self.assertEqual(10., self._metric.value())
