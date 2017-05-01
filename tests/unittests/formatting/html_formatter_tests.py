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

from hqlib.formatting import HTMLFormatter
from . import fake_domain, fake_report


class HTMLFormatterTest(unittest.TestCase):
    """ Unit tests for the html report formatter. """

    def setUp(self):
        self.__formatter = HTMLFormatter()

    def test_title_in_prefix(self):
        """ Test that the title is in the prefix. """
        self.assertTrue('<title>Report title</title>' in
                        self.__formatter.prefix(fake_report.Report([fake_domain.Product()])))

    def test_postfix(self):
        """ Test that the postfix closes the html tag. """
        self.assertTrue(self.__formatter.postfix().strip().endswith('</html>'))

    def test_section(self):
        """ Test that the report contains exactly one section. """
        html = self.__formatter.process(fake_report.Report())
        self.assertEqual(1, html.count('<h1>Section title'))

    def test_dashboard(self):
        """ Test that the report contains the dashboard. """
        html = self.__formatter.process(fake_report.Report())
        self.assertTrue("""<td colspan=1 rowspan=1 align="center" bgcolor="lightsteelblue">
                                        <div class="link_section_ID" title="Section title"></div>
                                        <div id="section_summary_chart_ID"></div>
                                    </td>""" in html)

    def test_metric_classes(self):
        """ Test that the report contains a list of metric classes it can report on. """
        html = self.__formatter.process(fake_report.Report())
        table_header = '<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>' \
                       '<th>Metriek (<code><small>Identifier</small></code>)</th><th>Norm</th>'
        self.assertTrue(table_header in html)

    def test_not_included_metric_classes(self):
        """ Test that the report shows which metric classes are included in the report and which are not. """
        html = self.__formatter.process(fake_report.Report())
        table_row = '<tr><td></td><td>Automatic regression test statement coverage ' \
                    '(<code><small>ARTStatementCoverage</small></code>)</td>'
        self.assertTrue(table_row in html)

    def test_metric_source_classes(self):
        """ Test that the report contains a list of metric source classes it can use. """
        html = self.__formatter.process(fake_report.Report())
        table_header = '<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>' \
                       '<th>Metriekbron (<code><small>Identifier</small></code>)</th><th>Instanties</th></tr>'
        self.assertTrue(table_header in html)

    def test_not_included_metric_source_class(self):
        """ Test that the report shows which metric source classes are included in the report and which are not. """
        html = self.__formatter.process(fake_report.Report())
        table_row = '<tr><td><span class="glyphicon glyphicon-ok" aria-hidden="true"></span></td><td>Git ' \
                    '(<code><small>Git</small></code>)</td><td><a href="http://git/" target="_blank">http://git/</a>' \
                    '</td></tr>'
        self.assertTrue(table_row in html)

    def test_requirements(self):
        """ Test that the report contains a list of requirements it can report on. """
        html = self.__formatter.process(fake_report.Report())
        table_header = '<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>' \
                       '<th>Eis (<code><small>Identifier</small></code>)</th><th>Metrieken</th></tr>'
        self.assertTrue(table_header in html)

    def test_not_included_requirements(self):
        """ Test that the report shows which requirements are included in the report and which are not. """
        html = self.__formatter.process(fake_report.Report())
        table_row = '<tr><td></td><td>Automated regression tests (<code><small>ART</small></code>)</td>'
        self.assertTrue(table_row in html)
        table_row = '<tr><td><span class="glyphicon glyphicon-ok" aria-hidden="true"></span></td>' \
                    '<td>Automated regression test coverage (<code><small>ARTCoverage</small></code>)</td>'
        self.assertTrue(table_row in html)

    def test_domain_objects(self):
        """ Test that the report contains a list of domain objects it can report on. """
        html = self.__formatter.process(fake_report.Report())
        table_header = '<table class="table table-striped first-col-centered">\n  <tr><th>In dit rapport?</th>' \
                       '<th>Domeinobject (<code><small>Identifier</small></code>)</th><th>Default eisen</th>' \
                       '<th>Optionele eisen</th></tr>'
        self.assertTrue(table_header in html)
