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


class FakeSonar(object):
    ''' Provide for a fake Sonar object so that the unit test don't need 
        access to an actual Sonar instance. '''
    # pylint: disable=unused-argument
    def __init__(self, line_coverage=0):
        self.__line_coverage = line_coverage
        
    def line_coverage(self, *args):
        ''' Return the percentage line coverage. '''
        return self.__line_coverage
    
    @staticmethod
    def unittests(*args):
        ''' Return the number of unittests. '''
        return 10
    
    @staticmethod
    def failing_unittests(*args):
        ''' Return the number of failing unittests. '''
        return 5
    
    @staticmethod
    def dashboard_url(*args):  
        ''' Return a fake dashboard url. '''
        return 'http://sonar'
       
    
class FakeSubject(object):  # pylint: disable=too-few-public-methods
    ''' Provide for a fake subject. '''
        
    def __repr__(self):
        return 'FakeSubject'
            
    @staticmethod
    def unittests():
        ''' Return the unit test Sonar id of the subject. '''
        return 'some:fake:id'
    

class SonarDashboardUrlTestMixin(object):  
    # pylint: disable=too-few-public-methods
    ''' Mixin for metrics whose url refers to the Sonar dashboard. '''
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())
               

class FailingUnittestsTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the failing unit tests metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        sonar = FakeSonar(line_coverage=89)
        self._metric = metric.FailingUnittests(subject=FakeSubject(),
                                               sonar=sonar, history=None)
    
    def test_value(self):
        ''' Test that the value of the metric equals the line coverage 
            reported by Sonar. '''
        self.assertEqual(5, self._metric.value())
        
    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('5 van de 10 unittests falen.', self._metric.report())


class UnittestCoverageTest(SonarDashboardUrlTestMixin, unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the unit test coverage metric. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        sonar = FakeSonar(line_coverage=89)
        self._metric = metric.UnittestCoverage(subject=FakeSubject(),
                                               sonar=sonar, history=None)
    
    def test_value(self):
        ''' Test that the value of the metric equals the line coverage 
            reported by Sonar. '''
        self.assertEqual(89, self._metric.value())
        
    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('FakeSubject unittest coverage is 89% (10 unittests).',
                         self._metric.report())
