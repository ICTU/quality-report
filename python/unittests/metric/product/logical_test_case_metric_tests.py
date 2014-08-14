'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import datetime
import unittest
from qualitylib import metric, domain, metric_source


class FakeBirt(object):
    ''' Provide for a fake Birt object. '''
    date_of_last_manual_tests = datetime.datetime.now() - \
        datetime.timedelta(days=5)

    def __init__(self, test_design=True):
        self.__test_design = test_design

    def has_test_design(self, birt_id):  # pylint: disable=unused-argument
        ''' Return whether the product with the Birt id has a test design 
            report in Birt. '''
        return self.__test_design

    @staticmethod
    def approved_ltcs(birt_id):  # pylint: disable=unused-argument
        ''' Return the number of approved logical test cases. '''
        return 100

    @staticmethod
    def nr_ltcs(birt_id):  # pylint: disable=unused-argument
        ''' Return the number of logical test cases. '''
        return 120

    @staticmethod
    def whats_missing_url(product):  # pylint: disable=unused-argument
        ''' Return the url for the what's missing report. '''
        return 'http://whats_missing'

    def date_of_last_manual_test(self, *args):
        # pylint: disable=unused-argument
        ''' Return the date that the manual test cases were last executed. '''
        return self.date_of_last_manual_tests

    @staticmethod
    def nr_manual_ltcs(birt_id, version='trunk'):
        # pylint: disable=unused-argument
        ''' Return the number of manual logical test cases. '''
        return 10

    @staticmethod
    def nr_manual_ltcs_too_old(birt_id, version, target):
        # pylint: disable=unused-argument
        ''' Return the number of manual logical test cases that haven't been
            executed recently enough. '''
        return 5

    @staticmethod
    def nr_automated_ltcs(birt_id):  # pylint: disable=unused-argument
        ''' Return the number of automated logical test cases. '''
        return 20

    @staticmethod
    def nr_ltcs_to_be_automated(birt_id):  # pylint: disable=unused-argument
        ''' Return the number of logical test cases that should be 
            automated. '''
        return 25

    @staticmethod  # pylint: disable=unused-argument
    def manual_test_execution_url(*args):
        ''' Return the url for the manual test execution report. '''
        return 'http://manual_tests'


class FakeSubject(object):
    ''' Provide for a fake subject. '''
    version = ''
    version_type = 'trunk'

    def __init__(self, birt_id=True, team=True, scrum_team=True):
        self.__birt_id = birt_id
        self.__team = team
        self.__scrum_team = scrum_team

    @staticmethod
    def name():
        ''' Return the name of the subject. '''
        return 'FakeSubject'

    def metric_source_id(self, metric_source):
        # pylint: disable=unused-argument
        ''' Return the Birt id of the subject. '''
        return 'birt id' if self.__birt_id else ''

    def product_version(self):
        ''' Return the version of the subject. '''
        return self.version

    def product_version_type(self):
        ''' Return the version type of the product. '''
        return self.version_type

    def responsible_teams(self, *args):  # pylint: disable-msg=unused-argument
        ''' Return the responsible teams for this product. '''
        return [domain.Team(name='Team', is_scrum_team=self.__scrum_team)] if \
            self.__team else []


class LogicalTestCasesNotAutomatedTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the logical test cases to be automated metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt:
                                                        self.__birt})
        self.__metric = metric.LogicalTestCasesNotAutomated( \
            subject=self.__subject, project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric is the percentage of user stories 
            that has enough logical test cases as reported by Birt. '''
        self.assertEqual(5, self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual(dict(Birt=self.__birt.whats_missing_url('product')), 
                         self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can  be measured when the project has Birt and
            the product has a Birt id and is a trunk version. '''
        self.failUnless(metric.LogicalTestCasesNotAutomated.\
                        can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric can not be measured when the project has no
            Birt. '''
        self.failIf(metric.LogicalTestCasesNotAutomated.\
                    can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        ''' Test that the metric can not be measured when the product has no
            Birt id. '''
        product = FakeSubject(birt_id=False)
        self.failIf(metric.LogicalTestCasesNotAutomated.\
                    can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        ''' Test that the metric can only be measured for trunk versions. '''
        product = FakeSubject(birt_id=False)
        product.version = '1.1'
        self.failIf(metric.LogicalTestCasesNotAutomated.\
                    can_be_measured(product, self.__project))


class LogicalTestCasesNotReviewedAndApprovedTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unapproved and/or unreviewed logical test cases 
        metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt:
                                                        birt})
        self.__metric = metric.LogicalTestCasesNotReviewedAndApproved( \
            subject=self.__subject, project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric is the number of not approved
            logical test cases as reported by Birt. '''
        self.assertEqual(20, self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('FakeSubject heeft 20 niet gereviewde en/of niet '
                         'goedgekeurde logische testgevallen van in totaal 120 '
                         'logische testgevallen.', self.__metric.report())

    def test_can_be_measured(self):
        ''' Test that the metric can  be measured when the project has Birt and
            the product has a Birt id and is a trunk version. '''
        self.failUnless(metric.LogicalTestCasesNotReviewedAndApproved.\
                        can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric can not be measured when the project has no
            Birt. '''
        self.failIf(metric.LogicalTestCasesNotReviewedAndApproved.\
                    can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        ''' Test that the metric can not be measured when the product has no
            Birt id. '''
        product = FakeSubject(birt_id=False)
        self.failIf(metric.LogicalTestCasesNotReviewedAndApproved.\
                    can_be_measured(product, self.__project))

    def test_cant_be_measured_for_released_product(self):
        ''' Test that the metric can only be measured for trunk versions. '''
        product = self.__subject
        product.version = '1.1'
        self.failIf(metric.LogicalTestCasesNotReviewedAndApproved.\
                    can_be_measured(product, self.__project))

    def test_cant_be_measured_without_test_design(self):
        ''' Test that the metric can not be measured if the product has no
            test design report in Birt. '''
        birt = FakeBirt(test_design=False)
        project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.failIf(metric.LogicalTestCasesNotReviewedAndApproved.\
                    can_be_measured(self.__subject, project))


class ManualLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ManualLogicalTestCases metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt:
                                                        self.__birt})
        self.__metric = metric.ManualLogicalTestCases( \
            subject=self.__subject, project=self.__project)

    def test_value(self):
        ''' Test that the value of the metric is the number of days ago that
            the manual logical test cases have been last executed as reported 
            by Birt. '''
        self.assertEqual(5, self.__metric.value())

    def test_value_when_untested(self):
        ''' Test that the value is large when the manual tests have not been 
            executed at all. '''
        self.__birt.date_of_last_manual_tests = datetime.datetime.min
        self.failUnless(self.__metric.value() > 100000)

    def test_value_when_release_untested(self):
        ''' Test that the value is the age of the release when the release has
            not been tested. '''
        self.__birt.date_of_last_manual_tests = datetime.datetime.min
        self.__subject.version = '1.1'
        expected_value = (datetime.datetime.now() - datetime.datetime.min).days
        self.assertEqual(expected_value, self.__metric.value())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless('5 van de 10 handmatige logische testgevallen van ' \
                        'FakeSubject zijn te lang geleden ' \
                        '(meest recente 5 dag(en), ' in self.__metric.report())

    def test_report_with_untested(self):
        ''' Test that the report mentions the number of test cases that have
            never been tested. '''
        self.__birt.date_of_last_manual_tests = datetime.datetime.now() - \
                                                datetime.timedelta(days=60)
        self.failUnless(self.__metric.report().startswith('5 van de 10 ' \
            'handmatige logische testgevallen van FakeSubject zijn te lang ' \
            'geleden (meest recente 60 dag(en), '))

    def test_report_when_untested(self):
        ''' Test that the report uses the correct template when the manual
            tests have not been executed at all. '''
        self.__birt.date_of_last_manual_tests = datetime.datetime.min
        self.assertEqual('De 10 handmatige logische testgevallen van ' \
                        'FakeSubject zijn nog nooit uitgevoerd.',
                        self.__metric.report())

    def test_target_when_release(self):
        ''' Test that the target is stricter for release candidates. '''
        self.__subject.version = '1.1'
        self.__subject.version_type = 'release'
        self.assertEqual(0, self.__metric.target())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Birt=self.__birt.manual_test_execution_url()), 
                         self.__metric.url())

    def test_can_be_measured(self):
        ''' Test that the metric can  be measured when the project has Birt and
            the product has a Birt id and is a trunk version. '''
        self.failUnless(metric.ManualLogicalTestCases.\
                        can_be_measured(self.__subject, self.__project))

    def test_cant_be_measured_without_birt(self):
        ''' Test that the metric can not be measured when the project has no
            Birt. '''
        self.failIf(metric.ManualLogicalTestCases.\
                    can_be_measured(self.__subject, domain.Project()))

    def test_cant_be_measured_without_birt_id(self):
        ''' Test that the metric can not be measured when the product has no
            Birt id. '''
        product = FakeSubject(birt_id=False)
        self.failIf(metric.ManualLogicalTestCases.\
                    can_be_measured(product, self.__project))

    def test_can_be_measured_for_released_product(self):
        ''' Test that the metric can only be measured for trunk versions. '''
        product = self.__subject
        product.version = '1.1'
        self.failUnless(metric.ManualLogicalTestCases.\
                        can_be_measured(product, self.__project))

    def test_cant_be_measured_without_responsible_teams(self):
        ''' Test that the metric can not be measured without responsible 
            team. '''
        product = FakeSubject(team=False)
        self.failIf(metric.ManualLogicalTestCases.\
                    can_be_measured(product, self.__project))
