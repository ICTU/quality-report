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

from qualitylib import metric, domain, metric_source


class FakeBirt(object):
    """ Provide for a fake Birt object. """
    date_of_last_manual_tests = datetime.datetime.now() - datetime.timedelta(days=5)

    def __init__(self, test_design=True):
        self.__test_design = test_design

    def has_test_design(self, birt_id):  # pylint: disable=unused-argument
        """ Return whether the product with the Birt id has a test design  report in Birt. """
        return self.__test_design

    @staticmethod
    def approved_ltcs(birt_id):  # pylint: disable=unused-argument
        """ Return the number of approved logical test cases. """
        return 100

    @staticmethod
    def nr_ltcs(birt_id):  # pylint: disable=unused-argument
        """ Return the number of logical test cases. """
        return 120

    @staticmethod
    def reviewed_ltcs(birt_id):  # pylint: disable=unused-argument
        """ Return the number of reviewed logical test cases. """
        return 110

    @staticmethod
    def whats_missing_url(product):  # pylint: disable=unused-argument
        """ Return the url for the what's missing report. """
        return 'http://whats_missing'

    def date_of_last_manual_test(self, *args):  # pylint: disable=unused-argument
        """ Return the date that the manual test cases were last executed. """
        return self.date_of_last_manual_tests

    @staticmethod
    def nr_manual_ltcs(birt_id, version='trunk'):  # pylint: disable=unused-argument
        """ Return the number of manual logical test cases. """
        return 10

    @staticmethod
    def nr_manual_ltcs_too_old(birt_id, version, target):  # pylint: disable=unused-argument
        """ Return the number of manual logical test cases that haven't been  executed recently enough. """
        return 5

    @staticmethod
    def nr_automated_ltcs(birt_id):  # pylint: disable=unused-argument
        """ Return the number of automated logical test cases. """
        return 20

    @staticmethod
    def nr_ltcs_to_be_automated(birt_id):  # pylint: disable=unused-argument
        """ Return the number of logical test cases that should be automated. """
        return 25

    @staticmethod
    def manual_test_execution_url(*args):  # pylint: disable=unused-argument
        """ Return the url for the manual test execution report. """
        return 'http://manual_tests'


class FakeSubject(object):
    """ Provide for a fake subject. """
    version = ''
    version_type = 'trunk'

    def __init__(self, birt_id=True, team=True, scrum_team=True):
        self.__birt_id = birt_id
        self.__team = team
        self.__scrum_team = scrum_team

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, metric_src):  # pylint: disable=unused-argument
        """ Return the Birt id of the subject. """
        return 'birt id' if self.__birt_id else ''

    def product_version(self):
        """ Return the version of the subject. """
        return self.version

    def product_version_type(self):
        """ Return the version type of the product. """
        return self.version_type


class LogicalTestCasesNotAutomatedTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the logical test cases to be automated metric. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.LogicalTestCasesNotAutomated(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the percentage of user stories that has enough logical test cases
            as reported by Birt. """
        self.assertEqual(5, self.__metric.value())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual(dict(Birt=self.__birt.whats_missing_url('product')), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can  be measured when the project has Birt and the product has a Birt id and
            is a trunk version. """
        self.assertTrue(metric.LogicalTestCasesNotAutomated.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric can not be measured when the project has no Birt. """
        self.assertFalse(metric.LogicalTestCasesNotAutomated.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric can not be measured when the product has no Birt id. """
        product = FakeSubject(birt_id=False)
        self.assertFalse(metric.LogicalTestCasesNotAutomated.can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = FakeSubject(birt_id=False)
        product.version = '1.1'
        self.assertFalse(metric.LogicalTestCasesNotAutomated.can_be_measured(product, self.__project))


class LogicalTestCasesNotReviewedTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the unreviewed logical test cases metric. """
    def setUp(self):
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.__metric = metric.LogicalTestCasesNotReviewed(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not reviewed logical test cases as reported by Birt. """
        self.assertEqual(10, self.__metric.value())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 10 niet gereviewde logische testgevallen van in totaal 120 '
                         'logische testgevallen.', self.__metric.report())

    def test_can_be_measured(self):
        """ Test that the metric can  be measured when the project has Birt and the product has a Birt id and is
            a trunk version. """
        self.assertTrue(metric.LogicalTestCasesNotReviewed.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric can not be measured when the project has no Birt. """
        self.assertFalse(metric.LogicalTestCasesNotReviewed.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric can not be measured when the product has no Birt id. """
        product = FakeSubject(birt_id=False)
        self.assertFalse(metric.LogicalTestCasesNotReviewed.can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.LogicalTestCasesNotReviewed.can_be_measured(product, self.__project))

    def test_cant_be_measured_without_test_design(self):
        """ Test that the metric can not be measured if the product has no test design report in Birt. """
        birt = FakeBirt(test_design=False)
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.assertFalse(metric.LogicalTestCasesNotReviewed.can_be_measured(self.__subject, project))


class LogicalTestCasesNotApprovedTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the unapproved logical test case metric. """
    def setUp(self):
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.__metric = metric.LogicalTestCasesNotApproved(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not approved logical test cases as reported by Birt. """
        self.assertEqual(10, self.__metric.value())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 10 niet goedgekeurde logische testgevallen van in totaal 110 gereviewde '
                         'logische testgevallen.', self.__metric.report())

    def test_can_be_measured(self):
        """ Test that the metric can  be measured when the project has Birt and the product has a Birt id and is
            a trunk version. """
        self.assertTrue(metric.LogicalTestCasesNotApproved.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric can not be measured when the project has no Birt. """
        self.assertFalse(metric.LogicalTestCasesNotApproved.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric can not be measured when the product has no Birt id. """
        product = FakeSubject(birt_id=False)
        self.assertFalse(metric.LogicalTestCasesNotApproved.can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.LogicalTestCasesNotApproved.can_be_measured(product, self.__project))

    def test_cant_be_measured_without_test_design(self):
        """ Test that the metric can not be measured if the product has no test design report in Birt. """
        birt = FakeBirt(test_design=False)
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.assertFalse(metric.LogicalTestCasesNotApproved.can_be_measured(self.__subject, project))


class ManualLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the ManualLogicalTestCases metric. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.ManualLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of days ago that the manual logical test cases have been
            last executed as reported by Birt. """
        self.assertEqual(5, self.__metric.value())

    def test_value_when_untested(self):
        """ Test that the value is the age of the version when the release has not been tested. """
        self.__birt.date_of_last_manual_tests = datetime.datetime.min
        expected_value = (datetime.datetime.now() - datetime.datetime.min).days
        self.assertEqual(expected_value, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertTrue('5 van de 10 handmatige logische testgevallen van FakeSubject zijn te lang geleden '
                        '(meest recente 5 dag(en), ' in self.__metric.report())

    def test_report_with_untested(self):
        """ Test that the report mentions the number of test cases that have never been tested. """
        self.__birt.date_of_last_manual_tests = datetime.datetime.now() - datetime.timedelta(days=60)
        self.assertTrue(
            self.__metric.report().startswith('5 van de 10 handmatige logische testgevallen van FakeSubject zijn '
                                              'te lang geleden (meest recente 60 dag(en), '))

    def test_report_when_untested(self):
        """ Test that the report uses the correct template when the manual tests have not been executed at all. """
        self.__birt.date_of_last_manual_tests = datetime.datetime.min
        self.assertEqual('De 10 handmatige logische testgevallen van FakeSubject zijn nog niet allemaal uitgevoerd.',
                         self.__metric.report())

    def test_target_when_release(self):
        """ Test that the target is stricter for release candidates. """
        self.__subject.version = '1.1'
        self.__subject.version_type = 'release'
        self.assertEqual(0, self.__metric.target())

    def test_url(self):
        """ Test that the url is correct. """
        self.assertEqual(dict(Birt=self.__birt.manual_test_execution_url()), self.__metric.url())

    def test_can_be_measured(self):
        """ Test that the metric can  be measured when the project has Birt and the product has a Birt id, the project
            has Subversion and the product has a Subversion id and the product is a trunk version. """
        self.assertTrue(metric.ManualLogicalTestCases.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric can not be measured when the project has no Birt. """
        self.assertFalse(metric.ManualLogicalTestCases.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric can not be measured when the product has no Birt id. """
        product = FakeSubject(birt_id=False)
        self.assertFalse(metric.ManualLogicalTestCases.can_be_measured(product, self.__project))

    def test_can_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertTrue(metric.ManualLogicalTestCases.can_be_measured(product, self.__project))


class NumberOfManualLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the NumberOfManualLogicalTestCases metric. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.NumberOfManualLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of manual logical test cases. """
        self.assertEqual(10, self.__metric.value())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('10 van de 120 logische testgevallen zijn handmatig.', self.__metric.report())

    def test_norm(self):
        """ Test the norm text. """
        self.assertEqual('Maximaal 10 van de logische testgevallen is handmatig. Meer dan 50 is rood.',
                         self.__metric.norm())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Birt and the product has a Birt id, and
            the product is a trunk version. """
        self.assertTrue(metric.NumberOfManualLogicalTestCases.can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        """ Test that the metric can not be measured when the project has no Birt. """
        self.assertFalse(metric.NumberOfManualLogicalTestCases.can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        """ Test that the metric can not be measured when the product has no Birt id. """
        product = FakeSubject(birt_id=False)
        self.assertFalse(metric.NumberOfManualLogicalTestCases.can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.NumberOfManualLogicalTestCases.can_be_measured(product, self.__project))

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())


class FakeJira(object):
    """ A fake Jira for testing purposes. """
    has_query = True

    def has_manual_test_cases_query(self):
        """ Return whether jira has a query for manual test cases. """
        return self.has_query

    @staticmethod
    def manual_test_cases_time():
        """ Return a fake duration of manual tests. """
        return 110

    @staticmethod
    def manual_test_cases_url():
        """ Return the url for the manual test case query. """
        return 'http://jira'

    @staticmethod
    def nr_manual_test_cases():
        """ Return the number of manual test cases. """
        return 5

    @staticmethod
    def nr_manual_test_cases_not_measured():
        """ Return the number of manual test cases whose duration hasn't been measured. """
        return 2


class DurationOfManualLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the DurationOfManualLogicalTestCases metric. """
    def setUp(self):
        self.__jira = FakeJira()
        self.__project = domain.Project(metric_sources={metric_source.Jira: self.__jira})
        self.__metric = metric.DurationOfManualLogicalTestCases(subject=self.__project, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the duration of the manual logical test cases. """
        self.assertEqual(110, self.__metric.value())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('De uitvoering van 3 van de 5 handmatige logische testgevallen kost 110 minuten.',
                         self.__metric.report())

    def test_norm(self):
        """ Test the norm text. """
        self.assertEqual('De uitvoering van de handmatige logische testgevallen kost maximaal 120 minuten. '
                         'Meer dan 240 is rood.', self.__metric.norm())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira and Jira has a manual test cases query. """
        self.assertTrue(metric.DurationOfManualLogicalTestCases.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric can not be measured when the project has no Jira. """
        project = domain.Project()
        self.assertFalse(metric.DurationOfManualLogicalTestCases.can_be_measured(project, project))

    def test_cant_be_measured_without_manual_test_query(self):
        """ Test that the metric can not be measured when Jira has no manual test cases query. """
        self.__jira.has_query = False
        self.assertFalse(metric.DurationOfManualLogicalTestCases.can_be_measured(self.__project, self.__project))

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Jira': 'http://jira'}, self.__metric.url())


class ManualLogicalTestCasesWithoutDurationTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the ManualLogicalTestCasesMeasured metric. """
    def setUp(self):
        self.__jira = FakeJira()
        self.__project = domain.Project(metric_sources={metric_source.Jira: self.__jira})
        self.__metric = metric.ManualLogicalTestCasesWithoutDuration(subject=self.__project, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of logical test cases not measured for duration. """
        self.assertEqual(2, self.__metric.value())

    def test_report(self):
        """ Test the metric report. """
        self.assertEqual('Van 2 van de 5 handmatige logische testgevallen is de uitvoeringstijd niet ingevuld.',
                         self.__metric.report())

    def test_norm(self):
        """ Test the norm text. """
        self.assertEqual('Van alle handmatige logische testgevallen is de uitvoeringstijd ingevuld.',
                         self.__metric.norm())

    def test_can_be_measured(self):
        """ Test that the metric can be measured when the project has Jira and Jira has a manual test cases query. """
        self.assertTrue(metric.ManualLogicalTestCasesWithoutDuration.can_be_measured(self.__project, self.__project))

    def test_cant_be_measured_without_jira(self):
        """ Test that the metric can not be measured when the project has no Jira. """
        project = domain.Project()
        self.assertFalse(metric.ManualLogicalTestCasesWithoutDuration.can_be_measured(project, project))

    def test_cant_be_measured_without_manual_test_query(self):
        """ Test that the metric can not be measured when Jira has no manual test cases query. """
        self.__jira.has_query = False
        self.assertFalse(metric.ManualLogicalTestCasesWithoutDuration.can_be_measured(self.__project, self.__project))

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Jira': 'http://jira'}, self.__metric.url())

