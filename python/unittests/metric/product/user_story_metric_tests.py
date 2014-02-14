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

import unittest
from qualitylib import metric
    
    
class FakeBirt(object):
    ''' Provide for a fake Birt object. '''
    
    @staticmethod
    def approved_user_stories(birt_id):  # pylint: disable=unused-argument
        ''' Return the number of approved user stories. '''
        return 20
    
    @staticmethod
    def nr_user_stories(birt_id):  # pylint: disable=unused-argument
        ''' Return the total number of user stories. '''
        return 25
    
    @staticmethod
    def nr_user_stories_with_sufficient_ltcs(birt_id):  
        # pylint: disable=unused-argument, invalid-name
        ''' Return the number of user stories with enough logical test 
            cases. '''
        return 23
        
    @staticmethod
    def whats_missing_url(product):  # pylint: disable=unused-argument
        ''' Return the url for the what's missing report. '''
        return 'http://whats_missing'
            
    
class FakeSubject(object):
    ''' Provide for a fake subject. '''
               
    @staticmethod
    def birt_id():
        ''' Return the Birt id of the subject. '''
        return ''
        

class ReviewedAndApprovedUserStoriesTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ReviewedAndApprovedUserStories metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__metric = metric.ReviewedAndApprovedUserStories( \
            subject=self.__subject, birt=birt, wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric is the percentage of approved
            user stories as reported by Birt. '''
        self.assertEqual(80, self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())


class UserStoriesWithEnoughLTCsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the user-stories-with-enough-logical-test-cases-
        metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__metric = metric.UserStoriesWithEnoughLogicalTestCases( \
            subject=self.__subject, birt=self.__birt, wiki=None, history=None)
        
    def test_value(self):
        ''' Test that the value of the metric is the percentage of user stories 
            that has enough logical test cases as reported by Birt. '''
        self.assertEqual(100*23/25., self.__metric.value())

    def test_url(self):
        ''' Test the url is correct. '''
        self.assertEqual(dict(Birt=self.__birt.whats_missing_url('product')), 
                         self.__metric.url())
