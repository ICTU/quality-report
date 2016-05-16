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

from qualitylib import domain


class MetricSourceTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the metric source domain class. """
    def test_default_name(self):
        """ Test the default name of a metric source. """
        self.assertEqual('Unknown metric source', domain.MetricSource().name())

    def test_given_name(self):
        """ Test that the name can be given as a parameter. """
        self.assertEqual('ABC', domain.MetricSource(name='ABC').name())


class MissingMetricSourceTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the missing metric source domain class. """
    def test_iteration(self):
        """ Test that missing metric sources are iterable. """
        for _ in domain.MissingMetricSource():  # pragma: no branch
            self.fail('Expected no items to iterate.')  # pragma: no cover
