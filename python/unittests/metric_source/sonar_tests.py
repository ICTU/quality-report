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
import StringIO
from qualitylib.metric_source import Sonar
from qualitylib.metric_source.sonar import SonarDashboard, SonarViolations, \
    SonarRunner


class FakeDashboard(object):  # pylint: disable=too-few-public-methods
    ''' Fake a Sonar dashboard. '''
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod  # pylint: disable=unused-argument
    def metric(*args, **kwargs):
        ''' Return a metric value. '''
        return 100
    
    @staticmethod  # pylint: disable=unused-argument
    def version(*args, **kwargs):
        ''' Return the version of a product. '''
        return '4.2'


class FakeViolations(object):  # pylint: disable=too-few-public-methods
    ''' Fake a Sonar violations page. '''
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod  # pylint: disable=unused-argument
    def violation(*args, **kwargs):
        ''' Return the number of violations. '''
        return 50


class SonarTest(unittest.TestCase):  
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = Sonar('http://sonar/', 
                             dashboard_class=FakeDashboard,
                             violations_class=FakeViolations)
        
    def test_url(self):
        ''' Test the url. '''
        self.assertEqual('http://sonar/', self.__sonar.url())
        
    def test_dashboard_url(self):
        ''' Test the url of a dashboard for a specific product. '''
        self.assertEqual('http://sonar/dashboard/index/product', 
                         self.__sonar.dashboard_url('product'))
        
    def test_violations_url(self):
        ''' Test the url of a violations page for a specific product. '''
        self.assertEqual('http://sonar/drilldown/violations/product', 
                         self.__sonar.violations_url('product'))
        
    def test_version(self):
        ''' Test that the version of a product is equal to the version returned
            by the dashboard of that product. '''
        self.assertEqual('4.2', self.__sonar.version('product'))
        
    def test_ncloc(self):
        ''' Test that the number of non-commented lines of code equals the 
            ncloc returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.ncloc('product'))
        
    def test_lines(self):
        ''' Test that the number of lines of code equals the number of lines
            returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.lines('product'))
        
    def test_major_violations(self):
        ''' Test that the number of major violations equals the number of major
            violations returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.major_violations('product'))

    def test_critical_violations(self):
        ''' Test that the number of critical violations equals the number of 
            critical violations returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.critical_violations('product'))
        
    def test_duplicated_lines(self):
        ''' Test that the number of duplicated lines equals the number of 
            duplicated lines returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.duplicated_lines('product'))

    def test_line_coverage(self):
        ''' Test that the line coverage equals the line coverage returned by 
            the dashboard. '''
        self.assertEqual(100, self.__sonar.line_coverage('product'))
        
    def test_unittests(self):
        ''' Test that the number of unit tests equals the number of unit tests 
            returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.unittests('product'))
         
    def test_failing_unittests(self):
        ''' Test that the number of failing unit tests equals the number of
            unit test failures plus the number of unit test errors returned
            by the dashboard. ''' 
        self.assertEqual(200, self.__sonar.failing_unittests('product'))

    def test_package_cycles(self):
        ''' Test that the number of package cycles equals the number of package
            cycles returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.package_cycles('product'))

    def test_methods(self):
        ''' Test that the number of methods equals the number of methods 
            returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.methods('product'))

    def test_commented_loc(self):
        ''' Test that the number of commented loc equals the number of 
            commented loc returned by the dashboard. '''
        self.assertEqual(100, self.__sonar.commented_loc('product'))
        
    def test_complex_methods(self):
        ''' Test that the number of complex methods equals the number of 
            complex methods returned by the violations page. '''
        self.assertEqual(50, self.__sonar.complex_methods('product'))
        
    def test_long_methods(self):
        ''' Test that the number of long methods equals the number of long
            methods returned by the violations page. '''
        self.assertEqual(50, self.__sonar.long_methods('product'))

    def test_many_parameters_methods(self):
        ''' Test that the number of methods with many parameters equals the 
            number of methods with many parameters returned by the violations
            page. '''
        self.assertEqual(50, self.__sonar.many_parameters_methods('product'))


class SonarDashboardUnderTest(SonarDashboard):
    ''' Override the url_open method to return fixed data. '''
    html = '<h4>Product 4.1</h4>'
    def url_open(self, url):
        return self.html


class SonarDashboardTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar dashboard page. '''
        
    def test_version(self):
        ''' Test the verion. '''
        SonarDashboardUnderTest.html = '<h4>Product 4.1</h4>'
        dashboard = SonarDashboardUnderTest('http://sonar/')
        self.assertEqual('4.1', dashboard.version())
        
    def test_version_error(self):
        ''' Test exception handling. '''
        SonarDashboardUnderTest.html = '<h4>Product3.1</h4>'
        dashboard = SonarDashboardUnderTest('http://sonar/')
        self.assertRaises(IndexError, dashboard.version)
        
    def test_metric(self):
        ''' Test retrieving a metric. '''
        SonarDashboardUnderTest.html = '<p id="m_metric1">10</p>'
        dashboard = SonarDashboardUnderTest('http://sonar/')
        self.assertEqual(10, dashboard.metric('metric1'))
        
    def test_metric_not_found(self):
        ''' Test that the default value is returned for a metric whose id 
            can not be found. '''
        SonarDashboardUnderTest.html = '<p id="m_metric1">10</p>'
        dashboard = SonarDashboardUnderTest('http://sonar/')
        self.assertEqual(5, dashboard.metric('metric2', default=5))


class SonarViolationsUnderTest(SonarViolations):
    ''' Override the url_open method to return fixed data. '''
    html = '<table id="col_rules"><tr></tr></table>'
    def url_open(self, url):
        return self.html


class SonarViolationsTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar violations page. '''
        
    def test_no_violation(self):
        ''' Test the default is returned when there are no violations. '''
        SonarViolationsUnderTest.html = '<table id="col_rules"><tr>' \
            '<td>No violations</td></tr></table>'
        violations = SonarViolationsUnderTest('http://sonar/')
        self.assertEqual(5, violations.violation('rule', 5))
        
    def test_violation(self):
        ''' Test the number of violations is returned when there are 
            violations. '''
        SonarViolationsUnderTest.html = '<table id="col_rules"><tr><td></td>' \
            '<td><a>rule</a></td><td><span>10</span></td></tr></table>'
        violations = SonarViolationsUnderTest('http://sonar/')
        self.assertEqual(10, violations.violation('rule'))
        
    def test_missing_rule(self):
        ''' Test the default is returned when there are no violations of the
            specified rule. '''
        SonarViolationsUnderTest.html = '<table id="col_rules"><tr><td></td>' \
            '<td><a>rule1</a></td><td><span>10</span></td></tr></table>'
        violations = SonarViolationsUnderTest('http://sonar/')
        self.assertEqual(0, violations.violation('rule2'))


class SonarRunnerUnderTest(SonarRunner):
    ''' Override SonarRunner to return a fake JSON string. '''
    def url_open(self, *args, **kwargs): # pylint: disable=unused-argument
        ''' Return a fake JSON string. '''
        return StringIO.StringIO('{}')
    
    
class SonarRunnerTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar runner that creates and deletes Sonar 
        analyses. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__runner = SonarRunnerUnderTest('http://sonar/')
        
    def test_analyse_products(self):
        ''' Test that the runner analyses products. '''
        self.__runner.analyse_products(set())
