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
from qualitylib import utils, metric_info
import copy
import logging
import os
import urllib2


class SonarRunner(beautifulsoup.BeautifulSoupOpener):
    ''' Class for creating and removing Sonar analyses. '''

    def __init__(self, sonar, maven, *args, **kwargs):
        super(SonarRunner, self).__init__(*args, **kwargs)
        self.__sonar = sonar
        self.__maven = maven
        self.__sonar_url = sonar.url()

    def analyse_products(self, products):
        ''' Run Sonar on the products and remove old analyses. '''
        sonar_analyses_to_keep = set()
        for product in products:
            self.__analyse_product(product)
            sonar_product_info = metric_info.SonarProductInfo(self.__sonar,
                                                              product)
            sonar_analyses_to_keep.update(sonar_product_info.all_sonar_ids())
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
        unittests = product.unittests()
        if unittests and unittests.sonar_id() != product.sonar_id() \
            and not self.__analysis_exists(unittests):
            # Need to run Sonar again for the unit test coverage:
            self.__checkout_code_and_run_sonar(unittests, unittests=True)
        jsf = product.jsf()
        if jsf and not self.__analysis_exists(jsf):
            self.__checkout_code_and_run_sonar(jsf)

    @utils.memoized
    def __analysis_exists(self, product):
        ''' Return whether a Sonar analysis for this product already exists. '''
        sonar_id = '"%s"' % product.sonar_id()
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
                try:
                    self.url_delete(self.__sonar_url + 'api/projects/%s' % \
                                    sonar_id)
                    logging.info('Removed Sonar analysis for %s', sonar_id)
                except urllib2.HTTPError, reason:
                    logging.warn("Can't remove Sonar analysis for %s: %s", 
                                 sonar_id, reason)

    def __checkout_code_and_run_sonar(self, product, unittests=False):
        ''' Check out the product and invoke Sonar through Maven. '''
        version = product.product_version()
        folder = product.name()
        if version:
            folder += '-' + version
        folder = folder.replace(':', '_')
        sonar_options = copy.copy(product.metric_source_options(self.__sonar)) \
            or dict()
        maven_options_string = product.metric_source_options(self.__maven) or ''
        if unittests:
            folder += '-unittests'
            maven_options_string += ' -Dut-coverage=true'
            sonar_branch = 'ut'
            if version:
                sonar_branch += ':' + version
            sonar_options['branch'] = sonar_branch
        else:
            if version:
                if 'branch' in sonar_options:
                    sonar_options['branch'] += ':' + version
                else:
                    sonar_options['branch'] = version
        sonar_options_string = ' '.join(['-Dsonar.%s=%s' % item \
                                         for item in sonar_options.items()])
        utils.rmtree(folder)  # Remove any left over checkouts
        product.check_out(folder)
        os.putenv('MAVEN_OPTS', '-Xmx2048m -XX:MaxPermSize=512m')
        maven_command = ('%s --fail-never clean install sonar:sonar ' % \
                         self.__maven.binary()) + \
                         sonar_options_string + ' ' + maven_options_string
        logging.info(maven_command)
        original_working_dir = os.getcwd()
        os.chdir(folder)
        os.system(maven_command)
        os.chdir(original_working_dir)
        utils.rmtree(folder)  # Remove folder to save space
