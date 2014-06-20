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


class SonarUnderTest(Sonar):  # pylint: disable=too-many-public-methods
    ''' Override the url open method to be able to return test data. '''

    json = '''
[
    {"version": "4.2", 
     "msr": 
         [
            {"val": 100, "rule_name": ""}, 
            {"val": 50, "rule_name": "Cyclomatic complexity"},
            {"val": 50, "rule_name": "Ncss Method Count"},
            {"val": 50, "rule_name": "Parameter Number"},
            {"val": 40, "rule_name": "Avoid commented-out lines of code"}
        ]
    }
]'''

    def url_open(self, url):
        return StringIO.StringIO(self.json)


class SonarTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Sonar class. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = SonarUnderTest('http://sonar/')

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
        self.assertEqual(40, self.__sonar.commented_loc('product'))

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

    def test_missing_metric_value(self):
        ''' Test that the default value is returned for missing values. '''
        self.__sonar.json = '[{"msr": []}]'
        self.assertEqual(0, self.__sonar.unittests('product'))

    def test_missing_violation_value(self):
        ''' Test that the default value is returned for missing violations. '''
        self.__sonar.json = '[{}]'
        self.assertEqual(0, self.__sonar.long_methods('product'))
