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

from hqlib.formatting import JSONFormatter
from . import fake_domain, fake_report


class FakeSonar(object):  # pylint: disable=too-few-public-methods
    """ Fake Sonar for unit testing purposes. """
    @staticmethod
    def version(*args):  # pylint: disable=unused-argument
        """ Return the version number of the component. """
        return '2'


class JSONFormatterTest(unittest.TestCase):
    """ Unit test for the dot report formatter class. """
    def setUp(self):
        self.__formatter = JSONFormatter(sonar=FakeSonar())

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.assertEqual(
            '{"date": "2012-01-01 12:00:00", "metric_id": ("15", "red", "2012-01-01 12:00:00"), '
            '"metric_id": ("15", "red", "2012-01-01 12:00:00"), }\n',
            self.__formatter.process(fake_report.Report()))

    def test_prefix_no_products(self):
        """ Test that the prefix is correct. """
        self.assertEqual('{"date": "2012-01-01 12:00:00", ', self.__formatter.prefix(fake_report.Report()))

    def test_prefix_product(self):
        """ Test that the prefix contains the version of the products that not have been released
            (i.e. the version of the trunk). """
        report = fake_report.Report([fake_domain.Product()])
        self.assertEqual('{"Product-version": "2", "date": "2012-01-01 12:00:00", ', self.__formatter.prefix(report))

    def test_formatting_error(self):
        """ Test that formatting a non-numerical value raises a type error. """

        class BuggyMetric(object):  # pylint: disable=too-few-public-methods
            """ A metric that returns a dummy string for every method called. """
            def __getattr__(self, attr):
                return lambda *args: 'dummy'

        self.assertRaises(ValueError, self.__formatter.metric, BuggyMetric())
