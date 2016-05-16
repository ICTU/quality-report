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

from qualitylib.formatting.base_formatter import Formatter
from unittests.formatting import fake_report, fake_domain


class FormatterUnderTest(Formatter):
    """ Implement abstract methods. """
    @staticmethod
    def prefix(*args, **kwargs):  # pylint: disable=unused-argument
        """ Return the prefix of the formatted report. """
        return '<prefix>'

    @staticmethod
    def metric(*args, **kwargs):  # pylint: disable=unused-argument
        """ Return a formatted metric. """
        return '<metric>'


class BaseFormatterTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the base report formatter. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__formatter = FormatterUnderTest()

    def test_process(self):
        """ Test that the report is processed. """
        report = fake_report.Report([fake_domain.Product()])
        self.assertEqual('<prefix><metric><metric>', self.__formatter.process(report))

    def test_postfix(self):
        """ Test that the postfix is empty. """
        self.assertEqual('', self.__formatter.postfix())
