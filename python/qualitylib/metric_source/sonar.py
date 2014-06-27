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

    def __init__(self, sonar_url, maven=None, *args, **kwargs):
        super(Sonar, self).__init__(url=sonar_url, *args, **kwargs)
        maven = maven or Maven()
        self.__runner = sonar_runner.SonarRunner(self, maven, *args, **kwargs)
        self.__base_dashboard_url = sonar_url + 'dashboard/index/'
        self.__base_violations_url = sonar_url + 'drilldown/violations/'
        self.__violations_api_url = sonar_url + 'api/resources?resource=%s&' \
            'metrics=blocker_violations,critical_violations,major_violations,' \
            'minor_violations,info_violations&rules=true&includetrends=true'
        self.__metrics_api_url = sonar_url + 'api/resources?resource=%s&' \
            'metrics=%s'

    @utils.memoized
    def version(self, product):
        ''' Return the version of the product. '''
        json = self.url_open(self.url() + \
                             'api/resources?resource=%s' % product).read()
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

    def duplicated_lines(self, product):
        ''' Return the number of duplicated lines for the product. '''
        return self.__metric(product, 'duplicated_lines')
 
    def line_coverage(self, product):
        ''' Return the line coverage of the unit tests for the product. '''
        return self.__metric(product, 'line_coverage')

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
        return self.__violation(product, 'Cyclomatic')

    def long_methods(self, product):
        ''' Return the number of methods in the product that have to many
            non-comment statements. '''
        return self.__violation(product, 'Ncss')

    def many_parameters_methods(self, product):
        ''' Return the number of methods in the product that have too many
            parameters. '''
        return self.__violation(product, 'Parameter Number')

    def commented_loc(self, product):
        ''' Return the number of commented out lines in the source code of
            the product. '''
        return self.__violation(product, 'commented-out')

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
            json = self.url_open(self.__metrics_api_url % (product, metric)).read()
        except urllib2.HTTPError, reason:
            logging.warning("Can't retrieve resource url %s from Sonar: %s",
                            self.__metrics_api_url % (product, metric), reason)
            return default
        try:
            return utils.eval_json(json)[0]['msr'][0]['val']
        except IndexError:
            logging.warning("Can't get %s value for %s from %s", metric, 
                            product, json)
            return default

    @utils.memoized
    def __violation(self, product, violation_name, default=0):
        ''' Return a specific violation value for the product. '''
        try:
            json = self.url_open(self.__violations_api_url % product).read()
        except urllib2.HTTPError, reason:
            logging.warning("Can't retrieve resource url %s from Sonar: %s",
                            self.__violations_api_url % product, reason)
            return default
        try:
            violations = utils.eval_json(json)[0]['msr']
        except (IndexError, KeyError):
            logging.warning("Can't get %s value for %s from %s", violation_name,
                            product, json)
            return default
        for violation in violations:
            if violation_name in violation['rule_name']:
                return violation['val']
        return default
