"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

import logging
import datetime
from datetime import timedelta

import unittest
from unittest.mock import patch, MagicMock

from hqlib import metric, domain, metric_source
from ..project.bug_metrics_tests import FakeJiraFilter


class LogicalTestCasesNotAutomatedTest(unittest.TestCase):
    """ Unit tests for the logical test cases to be automated metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.LogicalTestCasesNotAutomated(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the percentage of user stories that has enough logical test cases
            as reported by Birt. """
        self.__birt.nr_ltcs_to_be_automated.return_value = 25, []
        self.__birt.nr_automated_ltcs.return_value = 20, []
        self.assertEqual(5, self.__metric.value())

    def test_value_on_error(self):
        """ Test that the value is -1 when the metric source is not available. """
        self.__metric = metric.LogicalTestCasesNotAutomated(subject=self.__subject, project=domain.Project())
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.nr_ltcs_to_be_automated.return_value = 25, []
        self.__birt.nr_automated_ltcs.return_value = 20, []
        self.assertEqual('Er zijn 5 nog te automatiseren logische testgevallen, van in totaal 25 '
                         'geautomatiseerde logische testgevallen.', self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 9
        self.__subject.low_target.return_value = 15
        self.__birt.nr_ltcs_to_be_automated.return_value = -1, []
        self.__birt.nr_automated_ltcs.return_value = -1, []
        self.assertEqual("Maximaal 9 nog te automatiseren logische testgevallen. "
                         "Meer dan 15 nog te automatiseren logische testgevallen is rood.", self.__metric.norm())


class LogicalTestCasesNotReviewedTest(unittest.TestCase):
    """ Unit tests for the unreviewed logical test cases metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.LogicalTestCasesNotReviewed(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not reviewed logical test cases as reported by Birt. """
        self.__birt.nr_ltcs.return_value = 120, []
        self.__birt.reviewed_ltcs.return_value = 110, []
        self.assertEqual(10, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.nr_ltcs.return_value = 120, []
        self.__birt.reviewed_ltcs.return_value = 110, []
        self.assertEqual('Er zijn 10 niet gereviewde logische testgevallen, van in totaal 120 '
                         'logische testgevallen.', self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 0
        self.__subject.low_target.return_value = 15
        self.__birt.nr_ltcs.return_value = -1, []
        self.__birt.reviewed_ltcs.return_value = -1, []
        self.assertEqual("Maximaal 0 niet gereviewde logische testgevallen. "
                         "Meer dan 15 niet gereviewde logische testgevallen is rood.", self.__metric.norm())


class LogicalTestCasesNotApprovedTest(unittest.TestCase):
    """ Unit tests for the unapproved logical test case metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.LogicalTestCasesNotApproved(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not approved logical test cases as reported by Birt. """
        self.__birt.approved_ltcs.return_value = 100, []
        self.__birt.reviewed_ltcs.return_value = 110, []
        self.assertEqual(10, self.__metric.value())

    def test_value_with_ref(self):
        """ Test that the value of the metric is the number of not approved logical test cases as reported by Birt. """
        self.__birt.approved_ltcs.return_value = 0, []
        self.__birt.reviewed_ltcs.return_value = 1, [{"href": "xx/issue_key", "text": "unimportant"}]
        self.__birt.metric_source_urls.return_value = ['urls']
        self.__birt.metric_source_name = 'mock birt'
        self.assertEqual(1, self.__metric.value())
        self.assertEqual({'mock birt': 'urls'}, self.__metric.url())
        self.__birt.metric_source_urls.assert_called_once_with('issue_key')

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.approved_ltcs.return_value = 100, []
        self.__birt.reviewed_ltcs.return_value = 110, []
        self.assertEqual('Er zijn 10 niet goedgekeurde logische testgevallen, van in totaal 110 gereviewde '
                         'logische testgevallen.', self.__metric.report())

    def test_norm(self):
        """ Test that the norm is correct. """
        self.__subject.target.return_value = 0
        self.__subject.low_target.return_value = 10
        self.__birt.approved_ltcs.return_value = -1, []
        self.__birt.reviewed_ltcs.return_value = -1, []
        self.assertEqual("Maximaal 0 niet goedgekeurde logische testgevallen. "
                         "Meer dan 10 niet goedgekeurde logische testgevallen is rood.", self.__metric.norm())


class NumberOfManualLogicalTestCasesTest(unittest.TestCase):
    """ Unit tests for the NumberOfManualLogicalTestCases metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.NumberOfManualLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of manual logical test cases. """
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.__birt.nr_ltcs.return_value = 120, []
        self.assertEqual(10, self.__metric.value())

    @patch.object(logging, 'warning')
    def test_value_when_birt_missing(self, mock_warning):
        """ Test that the value is -1 when Birt is missing. """
        manual_ltcs = metric.NumberOfManualLogicalTestCases(subject=self.__subject, project=domain.Project())
        self.assertEqual(-1, manual_ltcs.value())
        mock_warning.assert_called_once()

    def test_report(self):
        """ Test the metric report. """
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.__birt.nr_ltcs.return_value = 120, []
        self.assertEqual('Er zijn 10 handmatige logische testgevallen, van in totaal 120 logische testgevallen.',
                         self.__metric.report())

    def test_norm(self):
        """ Test the norm text. """
        self.__subject.target.return_value = 10
        self.__subject.low_target.return_value = 50
        self.__birt.nr_manual_ltcs.return_value = -1, []
        self.__birt.nr_ltcs.return_value = -1, []
        self.assertEqual("Maximaal 10 handmatige logische testgevallen. "
                         "Meer dan 50 handmatige logische testgevallen is rood.", self.__metric.norm())


class ManualLogicalTestCasesTest(unittest.TestCase):
    """ Unit tests for the ManualLogicalTestCases metric. """
    def setUp(self):
        self.__birt = MagicMock()
        self.__subject = MagicMock()
        self.__project = domain.Project(metric_sources={metric_source.Backlog: self.__birt})
        self.__metric = metric.ManualLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of days ago that the manual logical test cases have been
            last executed as reported by Birt. """
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.now() - timedelta(days=5)
        self.assertEqual(5, self.__metric.value())

    def test_value_zero_ltcs(self):
        """ Test that the value of the metric is zero if there are no test cases. """
        self.__birt.nr_manual_ltcs.return_value = 0, []
        self.assertEqual(0, self.__metric.value())

    def test_value_when_untested(self):
        """ Test that the value is the age of the version when the release has not been tested. """
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime(2000, 1, 1)
        expected_value = (datetime.datetime.now() - datetime.datetime(2000, 1, 1)).days
        self.assertEqual(expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.__birt.nr_manual_ltcs_too_old.return_value = 5
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.now() - timedelta(days=5)
        self.assertTrue('5 van de 10 handmatige logische testgevallen zijn te lang geleden '
                        '(meest recente 5 dag(en))' in self.__metric.report())

    def test_report_with_untested(self):
        """ Test that the report mentions the number of test cases that have never been tested. """
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.now() - datetime.timedelta(days=60)
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.__birt.nr_manual_ltcs_too_old.return_value = 5
        self.assertTrue(
            self.__metric.report().startswith('5 van de 10 handmatige logische testgevallen zijn '
                                              'te lang geleden (meest recente 60 dag(en))'))

    def test_report_when_untested(self):
        """ Test that the report uses the correct template when the manual tests have not been executed at all. """
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.min
        self.__birt.nr_manual_ltcs.return_value = 10, []
        self.assertEqual('De 10 handmatige logische testgevallen zijn nog niet allemaal uitgevoerd.',
                         self.__metric.report())

    def test_report_without_manual_testcases(self):
        """ Test the report when there are no manual test cases. """
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.min
        self.__birt.nr_manual_ltcs.return_value = 0, []
        self.assertEqual(self.__metric.no_manual_tests_template.format(name='FakeSubject', unit=self.__metric.unit),
                         self.__metric.report())

    def test_status_without_manual_testcases_green(self):
        """ Test that the status is green when there are no manual test cases. """
        self.__birt.date_of_last_manual_test.return_value = datetime.datetime.now()
        self.__birt.nr_manual_tests = 0, []
        self.__subject.target.return_value = 5
        self.__subject.low_target.return_value = 15
        self.assertEqual('perfect', self.__metric.status())


class DurationOfManualLogicalTestCasesTest(unittest.TestCase):
    """ Unit tests for the DurationOfManualLogicalTestCases metric. """
    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.ManualLogicalTestCaseTracker: jira},
                                        metric_source_ids={jira: '12345'})
        self.__metric = metric.DurationOfManualLogicalTestCases(subject=self.__project, project=self.__project)

    @patch.object(metric_source.JiraFilter, 'issues_with_field')
    def test_value(self, issue_with_field_mock):
        """ Test that the value of the metric is the duration of the manual logical test cases. """
        jira_filter = metric_source.JiraFilter('http://jira/', 'username', 'password')
        issue_with_field_mock.return_value = [("issue1", 20), ("issue2", 60), ("issue3", 40)]
        self.__project = domain.Project(metric_sources={metric_source.ManualLogicalTestCaseTracker: jira_filter},
                                        metric_source_ids={jira_filter: '12345'})
        self.__metric = metric.DurationOfManualLogicalTestCases(subject=self.__project, project=self.__project)

        issue_with_field_mock.asses_called_once()
        self.assertEqual(120, self.__metric.value())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('De uitvoering van 8 van de 12 handmatige logische testgevallen kost 120 minuten.',
                         self.__metric.report())

    def test_report_without_jira(self):
        """ Test the metric report when no Jira filter has been configured. """
        self.assertEqual('De uitvoeringstijd van handmatige logische testgevallen van <no name> kon niet gemeten '
                         'worden omdat de bron ManualLogicalTestCaseTracker niet is geconfigureerd.',
                         metric.DurationOfManualLogicalTestCases(domain.Project(), domain.Project()).report())

    def test_norm(self):
        """ Test the norm text. """
        self.assertEqual('De uitvoering van de handmatige logische testgevallen kost maximaal 120 minuten. '
                         'Meer dan 240 minuten is rood.', self.__metric.norm())


class ManualLogicalTestCasesWithoutDurationTest(unittest.TestCase):
    """ Unit tests for the ManualLogicalTestCasesMeasured metric. """
    def setUp(self):
        jira = FakeJiraFilter()
        self.__project = domain.Project(metric_sources={metric_source.ManualLogicalTestCaseTracker: jira},
                                        metric_source_ids={jira: '12345'})
        self.__metric = metric.ManualLogicalTestCasesWithoutDuration(subject=self.__project, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of logical test cases not measured for duration. """
        self.assertEqual(4, self.__metric.value())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('Van 4 van de 12 handmatige logische testgevallen is de uitvoeringstijd niet ingevuld.',
                         self.__metric.report())

    def test_report_without_jira(self):
        """ Test the metric report when no Jira filter has been configured. """
        self.assertEqual('De hoeveelheid logische testgevallen zonder ingevulde uitvoeringstijd van <no name> kon niet '
                         'gemeten worden omdat de bron ManualLogicalTestCaseTracker niet is geconfigureerd.',
                         metric.ManualLogicalTestCasesWithoutDuration(domain.Project(), domain.Project()).report())

    def test_norm(self):
        """ Test the norm text. """
        self.assertEqual('Van alle handmatige logische testgevallen is de uitvoeringstijd ingevuld. '
                         'Meer dan 5 handmatige logische testgevallen niet ingevuld is rood.',
                         self.__metric.norm())
