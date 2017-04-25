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

from hqlib.report.section import Section, SectionHeader


class FakeMetric(object):
    """ Fake metric to use in the tests below. """

    @staticmethod
    def set_id_string(id_string):
        """ Ignore. """
        pass


class SectionHeaderTest(unittest.TestCase):
    """ Unit tests for the section header class. """

    def setUp(self):
        self.__header = SectionHeader('TE', 'title', 'subtitle')

    def test_title(self):
        """ Test that the title is correct. """
        self.assertEqual('title', self.__header.title())

    def test_subtitle(self):
        """ Test that the subtitle is correct. """
        self.assertEqual('subtitle', self.__header.subtitle())

    def test_id_prefix(self):
        """ Test that the id prefix is correct. """
        self.assertEqual('TE', self.__header.id_prefix())


class SectionTest(unittest.TestCase):
    """ Unit tests for the section class. """

    def setUp(self):
        self.__header = SectionHeader('TE', 'title', 'subtitle')
        self.__metrics = [FakeMetric(), FakeMetric()]
        self.__section = Section(self.__header, self.__metrics)

    def test_title(self):
        """ Test that the title of the section is the title of the header. """
        self.assertEqual(self.__header.title(), self.__section.title())

    def test_subtitle(self):
        """ Test that the subtitle of the section is the subtitle of the header. """
        self.assertEqual(self.__header.subtitle(), self.__section.subtitle())

    def test_id_prefix(self):
        """ Test that the id prefix of the section is the id prefix of the header. """
        self.assertEqual(self.__header.id_prefix(), self.__section.id_prefix())

    def test_str(self):
        """ Test that str(section) returns the title of the section. """
        self.assertEqual(self.__section.title(), str(self.__section))

    def test_get_metric(self):
        """ Test that the section is a list of metrics. """
        self.assertEqual(self.__metrics, list(self.__section))

    def test_get_all_metrics(self):
        """ Test that the section has a list of all metrics. """
        self.assertEqual(self.__metrics, self.__section.metrics())

    def test_product(self):
        """ Test that the section returns the product. """
        section = Section(None, [], product='Product')
        self.assertEqual('Product', section.product())
