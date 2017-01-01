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

from hqlib import domain


class MetricSourceTests(unittest.TestCase):
    """ Unit tests for the metric source domain class. """
    def test_default_name(self):
        """ Test the default name of a metric source. """
        self.assertEqual('Unknown metric source', domain.MetricSource().name())

    def test_given_name(self):
        """ Test that the name can be given as a parameter. """
        self.assertEqual('ABC', domain.MetricSource(name='ABC').name())

    def test_metric_source_url(self):
        """ Test that the metric source id is returned as url. """
        self.assertEqual(['http://url/to/subject'], domain.MetricSource().metric_source_urls('http://url/to/subject'))


class MissingMetricSourceTests(unittest.TestCase):
    """ Unit tests for the missing metric source domain class. """
    def test_iteration(self):
        """ Test that missing metric sources are iterable. """
        for _ in domain.MissingMetricSource():  # pragma: no branch
            self.fail('Expected no items to iterate.')  # pragma: no cover

    def test_url(self):
        """ Test that the missing metric source has no url. """
        self.assertEqual(None, domain.MissingMetricSource().url())
