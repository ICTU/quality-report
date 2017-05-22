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

import datetime
import unittest

from hqlib.formatting import JSONFormatter, MetricsFormatter, MetaMetricsHistoryFormatter, MetaDataJSONFormatter
from hqlib import utils, VERSION
from . import fake_domain, fake_report


class JSONFormatterTest(unittest.TestCase):
    """ Unit test for the dot report formatter class. """
    def setUp(self):
        self.__formatter = JSONFormatter()

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


class MetaMetricsHistoryFormatterTest(unittest.TestCase):
    """ Unit test for the meta metrics history to JSON formatter. """
    def setUp(self):
        self.__formatter = MetaMetricsHistoryFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.assertEqual('[[[2012, 3, 5, 16, 16, 58], [0, 1, 1, 0, 0, 0, 0]]]\n',
                         self.__formatter.process(fake_report.Report()))


class MetricsFormatterTest(unittest.TestCase):
    """ Unit test for the metrics to JSON formatter. """

    def setUp(self):
        self.__formatter = MetricsFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.maxDiff = None
        self.assertEqual('{{"report_date": [2012, 0, 1, 12, 0, 0], "report_title": "Report title", "hq_version": '
                         '"{0}", "sections": [{{"id": "id", "title": "Section title", '
                         '"subtitle": "Section subtitle"}}], "dashboard": {{"headers": [{{"header": "ME", '
                         '"colspan": 1}}], "rows": [[{{"section_id": "ID", "section_title": "Section title", '
                         '"bgcolor": "lightsteelblue", "colspan": 1, "rowspan": 1}}]]}}, '
                         '"metrics": [[{{"f": "id_string-1", "v": "id_string-01"}}, '
                         '"id_string", "red", "<img src=\'img/id_string-1.png\' border=\'0\' width=\'100\' '
                         'height=\'25\' />", {{"v": "0", "f": "<img src=\'img/sad.png\' alt=\':-(\' width=\'48\' '
                         'height=\'48\' title=\'Direct actie vereist: norm niet gehaald (sinds 1 januari 2012)\' '
                         'border=\'0\' />"}}, "report [label: <a href=\'http://url\' target=\'_blank\'>anchor</a>]", '
                         '"norm", "Comment with \\\\backslash"], [{{"f": "id_string-1", "v": "id_string-01"}}, '
                         '"id_string", "red", "<img src=\'img/id_string-1.png\' border=\'0\' width=\'100\' '
                         'height=\'25\' />", {{"v": "0", "f": "<img src=\'img/sad.png\' alt=\':-(\' width=\'48\' '
                         'height=\'48\' title=\'Direct actie vereist: norm niet gehaald (sinds 1 januari 2012)\' '
                         'border=\'0\' />"}}, "report [label: <a href=\'http://url\' target=\'_blank\'>anchor</a>]", '
                         '"norm", "Comment with \\\\backslash"]]}}\n'.format(VERSION),
                         self.__formatter.process(fake_report.Report()))

    def test_hover_unknown_start(self):
        """ Test that the hover text over the status icon explains the status and shows the start date of the
            status. """
        json = self.__formatter.process(fake_report.Report(metrics=[fake_domain.Metric()]))
        expected_date = utils.format_date(datetime.datetime(2012, 1, 1, 12, 0, 0), year=True)
        self.assertTrue("title='Direct actie vereist: norm niet gehaald (sinds {})".format(expected_date) in json)


class MetaDataFormatterTest(unittest.TestCase):
    """ Unit tests for the meta data JSON formatter. """
    def setUp(self):
        self.__formatter = MetaDataJSONFormatter()

    def test_process(self):
        """ Test that the report is processed correctly. """
        self.maxDiff = None
        self.assertEqual('{"domain_objects": [{"included": true, "name": "Document", "id": "Document", '
                         '"default_requirements": ["Track document age"], "optional_requirements": []}, '
                         '{"included": true, "name": "Product", "id": "Product", "default_requirements": [], '
                         '"optional_requirements": ["Automated regression test coverage", '
                         '"Automated regression tests", "Checkmarx SCA", "Code quality", "JSF code quality", '
                         '"OWASP Top 10 2013 Dependencies", "OWASP Top 10 2013 ZAP", "Performance endurance", '
                         '"Performance load", "Performance scalability", "Track branches", '
                         '"Unit and/or integration tests", "User stories and logical test cases"]}, {"included": true, '
                         '"name": "Project", "id": "Project", "default_requirements": [], '
                         '"optional_requirements": ["Track actions", "Track manual logical test cases", '
                         '"Track open bug reports", "Track ready user stories", "Track risks", "Track technical debt", '
                         '"Track whether user stories have security and performance risks", '
                         '"Trusted Product Maintainability, version 6.1"]}, {"included": true, "name": "Team", '
                         '"id": "Team", "default_requirements": ["Track spirit"], '
                         '"optional_requirements": ["Scrum team", "Track absence"]}], '
                         '"requirements": [{"included": true, "name": "Automated regression test coverage", '
                         '"id": "ARTCoverage", "metrics": ["Automatic regression test branch coverage", '
                         '"Automatic regression test statement coverage", "Coveragerapportageleeftijd"]}, '
                         '{"included": false, "name": "Automated regression tests", "id": "ART", "metrics": '
                         '["Hoeveelheid falende regressietesten", "Regressietestleeftijd"]}], "metrics": '
                         '[{"included": false, "name": "Automatic regression test statement coverage", '
                         '"id": "ARTStatementCoverage", "norm": "Minimaal 80% van de statements wordt gedekt door '
                         'geautomatiseerde functionele tests. Minder dan 70% is rood."}], "metric_sources": '
                         '[{"included": true, "name": "Git", "id": "Git", "urls": ["http://git/"]}]}\n',
                         self.__formatter.process(fake_report.Report()))
