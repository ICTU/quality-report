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

import datetime
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

    def test_datetime(self):
        """ Test that the datetime is now by default. """
        self.assertTrue(datetime.datetime.now() - domain.MetricSource().datetime() < datetime.timedelta(seconds=10))
