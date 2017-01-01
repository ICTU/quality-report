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
    def __init__(self, status=''):
        self.__status = status

    @staticmethod
    def set_id_string(id_string):
        """ Ignore. """
        pass

    def status(self):
        """ Return the preset status. """
        return self.__status


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
        self.__metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('yellow'), FakeMetric('grey'),
                          FakeMetric('red')]
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
        self.assertEqual(self.__metrics[0], self.__section[0])

    def test_get_all_metrics(self):
        """ Test that the section has a list of all metrics. """
        self.assertEqual(self.__metrics, self.__section.metrics())

    def test_color_red(self):
        """ Test that the section is red when one metric is red. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('red'), FakeMetric('grey'),
                   FakeMetric('yellow'), FakeMetric('missing')]
        section = Section(self.__header, metrics)
        self.assertEqual('red', section.color())

    def test_color_red_when_missing(self):
        """ Test that the section is red when one metric is missing and the rest is green or yellow. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('yellow'), FakeMetric('missing')]
        section = Section(self.__header, metrics)
        self.assertEqual('red', section.color())

    def test_color_red_when_missing_source(self):
        """ Test that the section is red when one metric source is missing and the rest is green or yellow. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('yellow'), FakeMetric('missing_source')]
        section = Section(self.__header, metrics)
        self.assertEqual('red', section.color())

    def test_color_yellow(self):
        """ Test that the section is yellow when no metrics are red and at least one is yellow. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('yellow'), FakeMetric('grey')]
        section = Section(self.__header, metrics)
        self.assertEqual('yellow', section.color())

    def test_color_grey(self):
        """ Test that the section is grey when no metrics are red or yellow and at least one is grey. """
        metrics = [FakeMetric('green'), FakeMetric('perfect'), FakeMetric('grey')]
        section = Section(self.__header, metrics)
        self.assertEqual('grey', section.color())

    def test_color_green(self):
        """ Test that the section is green when no metrics are red, yellow or grey. """
        metrics = [FakeMetric('green'), FakeMetric('perfect')]
        section = Section(self.__header, metrics)
        self.assertEqual('green', section.color())

    def test_color_perfect(self):
        """ Test that the section is green when all metrics are perfect. """
        metrics = [FakeMetric('perfect')]
        section = Section(self.__header, metrics)
        self.assertEqual('green', section.color())

    def test_color_white(self):
        """ Test that the section is white when it contains no metrics. """
        section = Section(self.__header, [])
        self.assertEqual('white', section.color())

    def test_has_no_history(self):
        """ Test that the section has no history unless its id prefix is MM (for Meta Metrics). """
        self.assertFalse(self.__section.has_history())

    def test_has_history(self):
        """ Test that the section has history when its id prefix is MM (for Meta Metrics). """
        section = Section(SectionHeader('MM', 'title', 'subtitle'), [])
        self.assertTrue(section.has_history())

    def test_history(self):
        """ Test that the section returns the history from the history metric source. """

        class FakeHistory(object):  # pylint: disable=too-few-public-methods
            """ Fake the history metric source. """
            @staticmethod
            def complete_history():
                """ Return a fake history. """
                return 'History'

        section = Section(None, [], history=FakeHistory())
        self.assertEqual('History', section.history())

    def test_product(self):
        """ Test that the section returns the product. """
        section = Section(None, [], product='Product')
        self.assertEqual('Product', section.product())
