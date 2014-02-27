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
from qualitylib import metric, domain

    
class FakeBirt(object):
    ''' Provide for a fake Birt object. '''
    date_of_last_manual_tests = datetime.datetime.now() - \
        datetime.timedelta(days=5)
                
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
        
    def __repr__(self):
        return 'FakeSubject'
    
    @staticmethod
    def birt_id():
        ''' Return the Birt id of the subject. '''
        return ''
         
    def product_version(self):
        ''' Return the version of the subject. '''
        return self.version
       
    @staticmethod
    def last_changed_date():
        ''' Return the date this product/version was last changed in the 
            source code repository. '''
        return datetime.datetime.now() - datetime.timedelta(days=2)
    
    @staticmethod  # pylint: disable-msg=unused-argument
    def responsible_teams(*args):
        ''' Return the responsible teams for this product. '''
        return [domain.Team('Team')]


class AutomatedLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the automated logical test cases metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__metric = metric.AutomatedLogicalTestCases( \
            subject=self.__subject, birt=self.__birt, wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric is the percentage of user stories 
            that has enough logical test cases as reported by Birt. '''
        self.assertEqual(100 * 20 / 25., self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual(dict(Birt=self.__birt.whats_missing_url('product')), 
                         self.__metric.url())


class ReviewedAndApprovedLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ReviewedAndApprovedLogicalTestCases metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__metric = metric.ReviewedAndApprovedLogicalTestCases( \
            subject=self.__subject, birt=birt, wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric is the percentage of approved
            logical test cases as reported by Birt. '''
        self.assertEqual(83, self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())


class ManualLogicalTestCasesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ManualLogicalTestCases metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__metric = metric.ManualLogicalTestCases( \
            subject=self.__subject, birt=self.__birt, wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric is the number of days ago that
            the manual logical test cases  have been last executed as reported 
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
        self.assertEqual(2, self.__metric.value())
        
    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless('5 van de 10 handmatige logische testgevallen van ' \
                        'FakeSubject zijn te lang geleden (5 dag(en), ' in 
                        self.__metric.report())
        
    def test_report_with_untested(self):
        ''' Test that the report mentions the number of test cases that have
            never been tested. '''
        self.__birt.date_of_last_manual_tests = datetime.datetime.now() - \
                                                datetime.timedelta(days=60)
        self.failUnless(self.__metric.report().startswith('5 van de 10 ' \
            'handmatige logische testgevallen van FakeSubject zijn te lang ' \
            'geleden (60 dag(en), '))
        
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Birt=self.__birt.manual_test_execution_url()), 
                         self.__metric.url())
