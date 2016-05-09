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

import datetime
import unittest

from qualitylib import utils
from qualitylib.formatting import HTMLFormatter
from unittests.formatting import fake_report, fake_domain


class HTMLFormatterTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the html report formatter. """

    def setUp(self):  # pylint: disable=invalid-name
        self.__formatter = HTMLFormatter()

    def test_title_in_prefix(self):
        """ Test that the title is in the prefix. """
        self.assertTrue('<title>Report title</title>' in
                        self.__formatter.prefix(fake_report.Report([fake_domain.Product()])))

    def test_postfix(self):
        """ Test that the postfix closes the html tag. """
        self.assertTrue(self.__formatter.postfix().endswith('</html>\n'))

    def test_section(self):
        """ Test that the report contains exactly one section. """
        html = self.__formatter.process(fake_report.Report())
        self.assertEqual(1, html.count('<h1>Section title'))

    def test_section_with_link(self):
        """ Test that the section can contain links. """
        product = fake_domain.Product(dependencies=True)
        html = self.__formatter.section(fake_report.Report(), fake_report.Section(product=product))
        self.assertTrue('%s:%s gebruikt:' % (product.name(), product.product_version()) in html)

    def test_one_metric(self):
        """ Test that the report contains one metric. """
        metric = fake_domain.Metric()
        html = self.__formatter.process(fake_report.Report(metrics=[metric]))
        self.assertTrue(metric.id_string() in html)

    def test_url(self):
        """ Test that the report contains the metric url. """
        metric = fake_domain.Metric()
        html = self.__formatter.process(fake_report.Report(metrics=[metric]))
        self.assertTrue('<a href="http://url" target="_blank">anchor</a>' in html)

    def test_meta_metrics(self):
        """ Test meta metrics. """
        html = self.__formatter.process(fake_report.Report(metrics=[fake_domain.Metric()]))
        for number in range(1, 5):
            self.assertTrue('MM-%d' % number in html, html)

    def test_project_resources(self):
        """ Test that the report contains the project resources. """
        html = self.__formatter.process(fake_report.Report())
        self.assertTrue('<li>resource: <a href="url">url</a></li>' in html)

    def test_missing_project_resource(self):
        """ Test that the report notes missing project resources. """
        html = self.__formatter.process(fake_report.Report())
        self.assertTrue('<li>missing: Geen url geconfigureerd</li>' in html)

    def test_dashboard(self):
        """ Test that the report contains the dashboard. """
        html = self.__formatter.process(fake_report.Report())
        self.assertTrue("""<td colspan=1 rowspan=1 align="center" bgcolor="lightsteelblue">
                                        <div class="link_section_ID" title="Section title"></div>
                                        <div id="section_summary_chart_ID"></div>
                                        <div id="section_summary_trunk_chart_ID"></div>
                                    </td>""" in html)

    def test_hover_unknown_start(self):
        """ Test that the hover text over the status icon explains the status and shows the start date of the
            status. """
        html = self.__formatter.process(fake_report.Report(metrics=[fake_domain.Metric()]))
        expected_date = utils.format_date(datetime.datetime(2012, 1, 1, 12, 0, 0), year=True)
        self.assertTrue('title="Direct actie vereist: norm niet gehaald of '
                        'meting te oud (sinds tenminste %s)' % expected_date in html)

    def test_hover_known_start(self):
        """ Test that the hover text over the status icon explains the status and shows the start date of the
            status. """
        expected_date = datetime.datetime(2014, 1, 1, 12, 0, 0)
        html = self.__formatter.process(
            fake_report.Report(metrics=[fake_domain.Metric(status_start_date=expected_date)]))
        expected_formatted_date = utils.format_date(expected_date, year=True)
        self.assertTrue('title="Direct actie vereist: norm niet gehaald of '
                        'meting te oud (sinds %s)' % expected_formatted_date in html)

    def test_product_meta_data_release_candidate(self):
        """ Test that the report shows whether a product is a release candidate. """
        release_candidate = fake_domain.Product(is_release_candidate=True)
        html = self.__formatter.process(fake_report.Report([release_candidate]))
        self.assertTrue(' is een releasekandidaat.</p>\n' in html)

    def test_product_meta_data_latest_release(self):
        """ Test that the report shows whether a product/version is the latest release of the product. """
        latest_release = fake_domain.Product(is_latest_release=True)
        html = self.__formatter.process(fake_report.Report([latest_release]))
        self.assertTrue(' is de meest recente versie.</p>\n' in html)

    def test_history(self):
        """ Test that the report contains the history of the meta metrics. """
        html = self.__formatter.process(fake_report.Report())
        self.assertTrue('new Date(2012, 3, 5, 16, 16, 58)' in html)

    def test_metric_classes(self):
        """ Test that the report contains a list of metric classes it can report on. """
        html = self.__formatter.process(fake_report.Report())
        table_header = '<table>\n<tr><th>Metriek</th><th>Class naam</th><th>Kwaliteitsattribuut</th><th>Norm</th>'
        self.assertTrue(table_header in html)
