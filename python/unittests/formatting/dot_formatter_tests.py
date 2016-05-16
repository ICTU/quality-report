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

from qualitylib import metric_source
from qualitylib.formatting import DependencyFormatter, MetricClassesFormatter
from unittests.formatting import fake_report, fake_domain


class CommonDotFormatterTestsMixin(object):  # pylint: disable=too-few-public-methods
    """ Tests for all dot graph formatters. """
    def test_postfix(self):
        """ Test that the formatter returns the correct postfix. """
        self.assertEqual('}\n', self._formatter.postfix())


class DependencyFormatterTest(CommonDotFormatterTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the dependency graph formatter class. """
    def setUp(self):
        self._formatter = DependencyFormatter()

    def test_prefix(self):
        """ Test that the formatter returns the correct prefix. """
        self.assertEqual('digraph { ranksep="2.5"; concentrate="true";', self._formatter.prefix(None))

    def test_body_empty_report(self):
        """ Test that the formatter returns """
        self.assertEqual('', self._formatter.body(fake_report.Report()))

    def test_body_one_product(self):
        """ Test that the body returns a graph with one product. """
        self.assertEqual('  subgraph "cluster-Fake Product" {\n'
                         '    label="Fake Product"; fillcolor="lightgrey"; '
                         'style="filled"\n'
                         '    "Fake Product:1" [label="1" style="filled" '
                         'fillcolor="green" URL="index.html#section_FP" '
                         'target="_top"];\n  };',
                         self._formatter.body(fake_report.Report([fake_domain.Product()])))

    def test_body_one_product_dependency(self):
        """ Test that the body returns a graph with one product dependency. """
        report = fake_report.Report([fake_domain.Product(True)])
        self.assertEqual('  subgraph "cluster-Fake Product" {\n'
                         '    label="Fake Product"; fillcolor="lightgrey"; '
                         'style="filled"\n'
                         '    "Fake Product:1" [label="1" style="filled" '
                         'fillcolor="green" URL="index.html#section_FP" '
                         'target="_top"];\n  };\n'
                         '  "Fake Product:1" -> "Fake Dependency:1";',
                         self._formatter.body(report))


class MetricClassFormatterTest(CommonDotFormatterTestsMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit test for the metric classes graph formatter class. """
    def setUp(self):
        self._formatter = MetricClassesFormatter()

    def test_prefix(self):
        """ Test that the formatter returns the correct prefix. """
        self.assertTrue(' rankdir=LR;' in self._formatter.prefix(None))

    def test_body(self):
        """ Test that the metrics of the report are listed. """
        self.assertEqual(""""Coverage report" [style="filled" fillcolor="red"];
"Automatic regression test statement coverage" [style="filled" fillcolor="red"];
"Coverage report" -> "Automatic regression test statement coverage";""",
                         self._formatter.body(fake_report.Report()))

    def test_body_green(self):
        """ Test that a metric is green when all metric sources are present. """
        jacoco = metric_source.JaCoCo()
        report = fake_report.Report(project_metric_sources={metric_source.CoverageReport: jacoco})
        self.assertEqual(""""Coverage report" [style="filled" fillcolor="green" URL="" target="_top"];
"Automatic regression test statement coverage" [style="filled" fillcolor="green"];
"Coverage report" -> "Automatic regression test statement coverage";""",
                         self._formatter.body(report))
