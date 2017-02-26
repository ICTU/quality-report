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

from hqlib import metric, domain, metric_source


class FakeSonar(object):
    """ Provide for a fake Sonar object so that the unit test don't need access to an actual Sonar instance. """
    # pylint: disable=unused-argument

    metric_source_name = metric_source.Sonar.metric_source_name

    @staticmethod
    def dashboard_url(*args):
        """ Return a fake dashboard url. """
        return 'http://sonar'

    @staticmethod
    def package_cycles(*args):
        """ Return the number of package cycles. """
        return 1


class CyclicDependenciesTest(unittest.TestCase):
    """ Unit tests for the cyclic dependencies metric. """

    def setUp(self):
        project = domain.Project(metric_sources={metric_source.Sonar: FakeSonar()})
        self.__subject = domain.Product(short_name='PR', name='FakeSubject')
        self._metric = metric.CyclicDependencies(subject=self.__subject, project=project)

    def test_value(self):
        """ Test that the value of the metric equals the number of cyclic dependencies between packages. """
        self.assertEqual(FakeSonar().package_cycles(), self._metric.value())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual({FakeSonar.metric_source_name: FakeSonar.dashboard_url()}, self._metric.url())
