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

from qualitylib.metric_source import beautifulsoup
from qualitylib import utils
import logging
import os


class SonarDashboard(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing a Sonar dashboard for a specific product. '''

    def __init__(self, url):
        super(SonarDashboard, self).__init__()
        self.__url = url
        self.__soup = self.soup(url)

    @utils.memoized
    def version(self):
        ''' Return the version of the product displayed on this Sonar
            dashboard. '''
        try:
            return self.__soup('h4')[0].string.strip().split(' ')[1]
        except IndexError:
            logging.error('Error parsing %s', self.__url)
            raise

    @utils.memoized
    def metric(self, metric_id, default=0):
        ''' Return the metric with the specified metric id. '''
        try:
            # Get the metric with metric_id and remove the thousands separator
            metric_text = self.__soup(id='m_' + metric_id)[0].string
            metric_value = float(metric_text.replace(',', '').replace('%', ''))
        except IndexError:
            metric_value = default  # Metric not found
        return metric_value


class SonarViolations(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Sonar violations page for a specific
        product. '''

    def __init__(self, url):
        super(SonarViolations, self).__init__()
        self.__soup = self.soup(url)

    @utils.memoized
    def violation(self, rule_name, default=0):
        ''' Return the number of violations for the specified rule. '''
        rules = self.__soup('table', id='col_rules')[0]('tr')
        if rules[0]('td')[0].string == 'No violations':
            return default
        violation = [rule for rule in rules if rule_name in \
                     rule('td')[1]('a')[0].string]
        if violation:
            number_of_violations = int(violation[0]('td')[2]('span')[0].string)
        else:
            number_of_violations = default
        return number_of_violations


class SonarRunner(beautifulsoup.BeautifulSoupOpener):
    ''' Class for creating and removing Sonar analyses. '''
    def __init__(self, sonar_url, *args, **kwargs):
        super(SonarRunner, self).__init__(*args, **kwargs)
        self.__sonar_url = sonar_url
        
    def analyse_products(self, products):
        ''' Run Sonar on the products and remove old analyses. '''
        sonar_analyses_to_keep = set()
        for product in products:
            self.__analyse_product(product)
            sonar_analyses_to_keep.update(product.all_sonar_ids())
        self.__remove_old_analyses(sonar_analyses_to_keep)

    def __analyse_product(self, product):
        ''' Run Sonar on the product, and unit tests if any. '''
        if not product.sonar_id():
            return
        if not self.__analysis_exists(product):
            users = ', '.join(['%s:%s' % (user.name(), 
                                          user.product_version() or 'trunk') \
                               for user in product.users()])
            logging.info('Check out and run sonar on %s:%s '
                         '(dependency of %s)', product.name(), 
                         product.product_version() or 'trunk', users or 'none')
            self.__checkout_code_and_run_sonar(product)
        if product.unittests() and product.unittests() != product.sonar_id() \
            and not self.__analysis_exists(product.unittests()):
            # Need to run Sonar again for the unit test coverage:
            self.__checkout_code_and_run_sonar(product, unittests=True)
        jsf = product.jsf()
        if jsf and not self.__analysis_exists(jsf):
            self.__checkout_code_and_run_sonar(jsf)

    @utils.memoized
    def __analysis_exists(self, product):
        ''' Return whether a Sonar analysis for this product already exists. '''
        sonar_id = '"%s"' % str(product)
        result = sonar_id in str(self.soup(self.__sonar_url + 'api/resources'))
        logging.info('Sonar analysis for %s %s', sonar_id,
                      {True: 'exists', False: 'does not exist'}[result])
        return result

    def __remove_old_analyses(self, sonar_analyses_to_keep):
        ''' Remove Sonar analyses that are no longer needed. '''
        
        def sonar_id_contains_version(sonar_id):
            ''' Return whether the Sonar id contains a version number. '''
            last_part = sonar_id.split(':')[-1]
            return len(last_part) > 0 and (last_part[0].isdigit() or \
                                           last_part[-1].isdigit())
        
        logging.debug('Removing Sonar analyses, keeping %s', 
                      sonar_analyses_to_keep)
        analyses = utils.eval_json(self.url_open(self.__sonar_url + \
                                                 'api/resources').read())
        for analysis in analyses:
            sonar_id = analysis['key']
            if sonar_id_contains_version(sonar_id) and \
               sonar_id not in sonar_analyses_to_keep and \
               sonar_id.rsplit(':', 1)[0] in sonar_analyses_to_keep:
                logging.info('Removing Sonar analysis for %s', sonar_id)
                self.url_delete(self.__sonar_url + 'api/projects/%s' % sonar_id)

    @staticmethod
    def __checkout_code_and_run_sonar(product, unittests=False):
        ''' Check out the product and invoke Sonar through Maven. '''
        version = product.product_version()
        folder = product.name()
        if version:
            folder += '-' + version
        folder = folder.replace(':', '_')
        sonar_options = product.sonar_options()
        if unittests:
            folder += '-unittests'
            maven_options_string = '-Dut-coverage=true ' + \
                                   product.unittest_maven_options()
            sonar_branch = 'ut'
            if version:
                sonar_branch += ':' + version
            sonar_options['branch'] = sonar_branch
        else:
            maven_options_string = product.maven_options()
            if version:
                if 'branch' in sonar_options:
                    sonar_options['branch'] += ':' + version
                else:
                    sonar_options['branch'] = version
        sonar_options_string = ' '.join(['-Dsonar.%s=%s' % item \
                                         for item in sonar_options.items()])
        utils.rmtree(folder)  # Remove any left over checkouts
        product.check_out(folder)
        maven_command = ('export MAVEN_OPTS="-Xmx2048m -XX:MaxPermSize=512m"; '
                         'cd %s; %s --fail-never clean install sonar:sonar ' % \
                         (folder, product.maven_binary())) + \
                         sonar_options_string + ' ' + maven_options_string
        if product.java_home():
            maven_command = 'export JAVA_HOME="%s"; ' % product.java_home() + \
                maven_command
        logging.info(maven_command)
        os.system(maven_command)
        utils.rmtree(folder)  # Remove folder to save space


class Sonar(beautifulsoup.BeautifulSoupOpener):
    ''' Class representing the Sonar instance. '''

    def __init__(self, sonar_url, dashboard_class=SonarDashboard, 
                 violations_class=SonarViolations, *args, **kwargs):
        super(Sonar, self).__init__(*args, **kwargs)
        self.__sonar_url = sonar_url
        self.__runner = SonarRunner(sonar_url, *args, **kwargs)
        self.__base_dashboard_url = sonar_url + 'dashboard/index/'
        self.__base_violations_url = sonar_url + 'drilldown/violations/'
        self.__dashboard_class = dashboard_class
        self.__violations_class = violations_class
                                     
    def url(self):
        ''' Return the base url for Sonar. '''
        return self.__sonar_url

    @utils.memoized
    def version(self, product):
        ''' Return the version of the product. '''
        result = self.__dashboard(product).version()
        logging.debug('Retrieving Sonar version for %s -> %s', product, result)
        return result

    #  Metrics

    @utils.memoized
    def ncloc(self, product):
        ''' Non-comment lines of code. '''
        return self.__dashboard(product).metric('ncloc')

    def lines(self, product):
        ''' Bruto lines of code, including comments, whitespace, javadoc. '''
        return self.__dashboard(product).metric('lines')

    def major_violations(self, product):
        ''' Return the number of major violations for the product. '''
        return self.__dashboard(product).metric('major_violations')

    def critical_violations(self, product):
        ''' Return the number of critical violations for the product. '''
        return self.__dashboard(product).metric('critical_violations')

    def duplicated_lines(self, product):
        ''' Return the number of duplicated lines for the product. '''
        return self.__dashboard(product).metric('duplicated_lines')

    def line_coverage(self, product):
        ''' Return the line coverage of the unit tests for the product. '''
        return self.__dashboard(product).metric('line_coverage')

    def unittests(self, product):
        ''' Return the number of unit tests for the product. '''
        return self.__dashboard(product).metric('tests')
    
    def failing_unittests(self, product):
        ''' Return the number of failing unit tests for the product. '''
        return self.__dashboard(product).metric('test_failures') + \
               self.__dashboard(product).metric('test_errors')
    
    def package_cycles(self, product):
        ''' Return the number of cycles in the package dependencies for the
            product. '''
        return self.__dashboard(product).metric('package_cycles')

    def methods(self, product):
        ''' Return the number of methods/functions in the product. '''
        return self.__dashboard(product).metric('functions')

    def commented_loc(self, product):
        ''' Return the number of commented out lines in the source code of
            the product. '''
        return self.__dashboard(product).metric('commented_out_code_lines')

    def dashboard_url(self, product):
        ''' Return the url for the Sonar dashboard for the product. '''
        return self.__base_dashboard_url + product

    # Violations

    def complex_methods(self, product):
        ''' Return the number of methods that violate the Cyclomatic complexity
            threshold. '''
        return self.__violations(product).violation('Cyclomatic')

    def long_methods(self, product):
        ''' Return the number of methods in the product that have to many
            non-comment statements. '''
        return self.__violations(product).violation('Ncss')

    def many_parameters_methods(self, product):
        ''' Return the number of methods in the product that have too many
            parameters. '''
        return self.__violations(product).violation('Parameter Number')

    def violations_url(self, product):
        ''' Return the url for the violations of the product. '''
        return self.__base_violations_url + product

    # Analysis
    
    def analyse_products(self, products):
        ''' Run Sonar on the products and remove old analyses. '''
        self.__runner.analyse_products(products)

    # Helper methods

    @utils.memoized
    def __dashboard(self, product):
        ''' Return the dashboard for the product. '''
        return self.__dashboard_class(self.dashboard_url(product))

    @utils.memoized
    def __violations(self, product):
        ''' Return the violations page for the product. '''
        return self.__violations_class(self.violations_url(product))
