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
from qualitylib import metric
       
    
class FakeEmma(object):
    ''' Fake Emma. '''
    url = 'http://emma'
    
    @staticmethod
    def coverage(emma_id):  # pylint: disable=unused-argument
        ''' Return the ART coverage. '''
        return 98
    
    @classmethod
    def get_coverage_url(cls, emma_id):  # pylint: disable=unused-argument
        ''' Return a fake url. '''
        return cls.url
    
    @staticmethod
    def coverage_date(emma_id):  # pylint: disable=unused-argument
        ''' Return a fake date. '''
        return datetime.datetime.today() - datetime.timedelta(days=4)


class FakeJaCoCo(FakeEmma):
    ''' Fake JaCoCo. '''
    url = 'http://jacoco'
          
    
class FakeSubject(object):
    ''' Provide for a fake subject. '''
    version = ''
    
    def __init__(self, emma_id=None, jacoco_id=None):
        self.__emma_id = emma_id
        self.__jacoco_id = jacoco_id
    
    def __repr__(self):
        return 'FakeSubject'
                
    def product_version(self):
        ''' Return the version of the subject. '''
        return self.version

    def art_coverage_emma(self):
        ''' Return the Emma id of the subject. '''
        return self.__emma_id
    
    def art_coverage_jacoco(self):
        ''' Return the JaCoCo id of the subject. '''
        return self.__jacoco_id 
    
    @staticmethod
    def birt_id():
        ''' Return the Birt id of the subject. '''
        return 'birt_id'


class ARTCoverageJacocoTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__jacoco = FakeJaCoCo()
        self.__subject = FakeSubject(jacoco_id='jacoco_id')
        self.__subject.version = '1.1'
        self.__metric = metric.ARTCoverage(subject=self.__subject, 
                                           jacoco=self.__jacoco, wiki=None, 
                                           history=None)
        
    def test_value(self):
        ''' Test that value of the metric equals the coverage as reported by
            Emma. '''
        self.assertEqual(self.__jacoco.coverage(None), self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(JaCoCo='http://jacoco'), self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless(self.__metric.report().startswith('FakeSubject ART ' \
                                                          'coverage is 98%'))
        
        
class ARTCoverageEmmaTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject(emma_id='emma_id')
        self.__emma = FakeEmma()
        self.__metric = metric.ARTCoverage(subject=self.__subject, 
                                           emma=self.__emma, wiki=None, 
                                           history=None)

    def test_value(self):
        ''' Test that value of the metric equals the coverage as reported by
            Emma. '''
        self.assertEqual(self.__emma.coverage(None), self.__metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Emma='http://emma'), self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.failUnless(self.__metric.report().startswith('FakeSubject ART ' \
                                                          'coverage is 98%'))


class FakeBirt(object):
    ''' Fake a Birt instance. '''
    @staticmethod
    def nr_performance_pages(product, version):
        ''' Return the number of pages. '''
        # pylint: disable=unused-argument
        return 10
    
    @staticmethod
    def nr_slow_performance_pages(product, version):
        ''' Return the number of slow pages. '''
        # pylint: disable=unused-argument
        return 3
    
    @staticmethod
    def page_performance_url(product, version):
        ''' Return the url for the page performance report. '''
        return 'http://birt/performance/%s/%s' % (product, version)
    

class ARTPerformanceTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the ART coverage metric. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__subject = FakeSubject()
        self.__birt = FakeBirt()
        self.__metric = metric.ARTPerformance(subject=self.__subject, 
                                              birt=self.__birt, wiki=None, 
                                              history=None)

    def test_value(self):
        ''' Test that value of the metric equals the percentage too slow pages
            as reported by Birt. '''
        expected = self.__birt.nr_slow_performance_pages('product', 
                                                         'version') / \
            float(self.__birt.nr_performance_pages('product', 'version')) * 100
        self.assertEqual(expected, self.__metric.value())

    def test_url(self):
        ''' Test that the url correctly points to the Birt report. '''
        self.assertEqual({'Birt': self.__birt.page_performance_url('birt_id', 
                                                                   'trunk')},
                         self.__metric.url())

    def test_report(self):
        ''' Test that the report for the metric is correct. '''
        self.assertEqual('30% (3 van de 10) van de paginas van FakeSubject ' \
                         'laadt te langzaam bij het uitvoeren van de ART.', 
                         self.__metric.report())
