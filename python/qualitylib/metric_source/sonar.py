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

from qualitylib.metric_source import url_opener, sonar_runner
from qualitylib.metric_source.maven import Maven
from qualitylib import utils, domain
import logging
import urllib2


class Sonar(domain.MetricSource, url_opener.UrlOpener):
    ''' Class representing the Sonar instance. '''

    metric_source_name = 'SonarQube'

    def __init__(self, sonar_url, maven=None, subversion=None, *args, **kwargs):
        super(Sonar, self).__init__(url=sonar_url, *args, **kwargs)
        maven = maven or Maven()
        self.__runner = sonar_runner.SonarRunner(self, maven, subversion, 
                                                 *args, **kwargs)
        self.__base_dashboard_url = sonar_url + 'dashboard/index/'
        self.__base_violations_url = sonar_url + 'drilldown/violations/'
        self.__violations_api_url = sonar_url + 'api/resources?resource=%s&' \
            'metrics=blocker_violations,critical_violations,major_violations,' \
            'minor_violations,info_violations&rules=true&includetrends=true'
        self.__resource_api_url = sonar_url + 'api/resources?resource=%s'
        self.__metrics_api_url = self.__resource_api_url + '&metrics=%s'

    @utils.memoized
    def version(self, product):
        ''' Return the version of the product. '''
        json = self.url_open(self.__resource_api_url % product).read()
        version = utils.eval_json(json)[0]['version']
        logging.debug('Retrieving Sonar version for %s -> %s', product, version)
        return version

    #  Metrics

    @utils.memoized
    def ncloc(self, product):
        ''' Non-comment lines of code. '''
        return self.__metric(product, 'ncloc')

    def lines(self, product):
        ''' Bruto lines of code, including comments, whitespace, javadoc. '''
        return self.__metric(product, 'lines')

    def major_violations(self, product):
        ''' Return the number of major violations for the product. '''
        return self.__metric(product, 'major_violations')

    def critical_violations(self, product):
        ''' Return the number of critical violations for the product. '''
        return self.__metric(product, 'critical_violations')

    def blocker_violations(self, product):
        ''' Return the number of blocker violations for the product. '''
        return self.__metric(product, 'blocker_violations')

    def duplicated_lines(self, product):
        ''' Return the number of duplicated lines for the product. '''
        return self.__metric(product, 'duplicated_lines')
 
    def line_coverage(self, product):
        ''' Return the line coverage of the unit tests for the product. '''
        return self.__metric(product, 'line_coverage')

    def branch_coverage(self, product):
        ''' Return the branch coverage of the unit tests for the product. '''
        return self.__metric(product, 'branch_coverage')

    def unittests(self, product):
        ''' Return the number of unit tests for the product. '''
        return self.__metric(product, 'tests')

    def failing_unittests(self, product):
        ''' Return the number of failing unit tests for the product. '''
        return self.__metric(product, 'test_failures') + \
               self.__metric(product, 'test_errors')

    def package_cycles(self, product):
        ''' Return the number of cycles in the package dependencies for the
            product. '''
        return self.__metric(product, 'package_cycles')

    def methods(self, product):
        ''' Return the number of methods/functions in the product. '''
        return self.__metric(product, 'functions')

    def dashboard_url(self, product):
        ''' Return the url for the Sonar dashboard for the product. '''
        return self.__base_dashboard_url + product

    # Violations

    def complex_methods(self, product):
        ''' Return the number of methods that violate the Cyclomatic complexity
            threshold. '''
        nr_complex_methods = 0
        violation_names = ('Cyclomatic', 'FunctionComplexity')
        for violation_name in violation_names:
            nr_complex_methods += self.__violation(product, violation_name)
        return nr_complex_methods

    def long_methods(self, product):
        ''' Return the number of methods in the product that have to many
            non-comment statements. '''
        nr_long_methods = 0
        violation_names = ('Ncss', 'AvoidLongMethodsRule', 'S138')
        for violation_name in violation_names:
            nr_long_methods += self.__violation(product, violation_name)
        return nr_long_methods

    def many_parameters_methods(self, product):
        ''' Return the number of methods in the product that have too many
            parameters. '''
        nr_many_parameters = 0
        violation_names = ('Parameter Number', 'AvoidLongParameterListsRule',
                           'ExcessiveParameterList')
        for violation_name in violation_names:
            nr_many_parameters += self.__violation(product, violation_name)
        return nr_many_parameters

    def commented_loc(self, product):
        ''' Return the number of commented out lines in the source code of
            the product. '''
        nr_commented_loc = 0
        violation_names = ('commented-out', 'CommentedCode')
        for violation_name in violation_names:
            nr_commented_loc += self.__violation(product, violation_name)
        return nr_commented_loc

    def violations_url(self, product):
        ''' Return the url for the violations of the product. '''
        return self.__base_violations_url + product

    # Analysis

    def analyse_products(self, products):
        ''' Run Sonar on the products and remove old analyses. '''
        self.__runner.analyse_products(products)

    # Helper methods

    @utils.memoized
    def __metric(self, product, metric, default=0):
        ''' Return a specific metric value for the product. '''
        try:
            json = self.__get_json(self.__metrics_api_url % (product, metric))
        except urllib2.HTTPError:
            return default
        try:
            return json[0]['msr'][0]['val']
        except IndexError:
            logging.warning("Can't get %s value for %s from %s", metric, 
                            product, json)
        return default

    @utils.memoized
    def __violation(self, product, violation_name, default=0):
        ''' Return a specific violation value for the product. '''
        try:
            json = self.__get_json(self.__violations_api_url % product)
        except urllib2.HTTPError:
            return default
        try:
            violations = json[0]['msr']
        except (IndexError, KeyError):
            logging.warning("Can't get %s value for %s from %s", violation_name,
                            product, json)
            return default
        for violation in violations:
            if violation_name in violation['rule_name'] or \
               violation_name in violation['rule_key']:
                return violation['val']
        return default

    def __get_json(self, url):
        ''' Get and evaluate the json from the url. '''
        try:
            json_string = self.url_open(url).read()
        except urllib2.HTTPError, reason:
            logging.warning("Can't retrieve resource url %s from Sonar: %s",
                            url, reason)
            raise
        return utils.eval_json(json_string)
