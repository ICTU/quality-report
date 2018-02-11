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

from hqlib.formatting import Formatter
from hqlib.domain import Product, Metric
from hqlib.report import QualityReport
from . import fake_report


class FormatterUnderTest(Formatter):
    """ Implement abstract methods. """
    def prefix(self, report: QualityReport) -> str:  # pylint: disable=unused-argument
        """ Return the prefix of the formatted report. """
        return '<prefix>'

    def metric(self, metric: Metric) -> str:   # pylint: disable=unused-argument
        """ Return a formatted metric. """
        return '<metric>'


class BaseFormatterTest(unittest.TestCase):
    """ Unit tests for the base report formatter. """

    def setUp(self):
        self.__formatter = FormatterUnderTest()

    def test_process(self):
        """ Test that the report is processed. """
        report = fake_report.Report([Product()])
        self.assertEqual('<prefix><metric><metric>', self.__formatter.process(report))

    def test_postfix(self):
        """ Test that the postfix is empty. """
        self.assertEqual('', self.__formatter.postfix())
