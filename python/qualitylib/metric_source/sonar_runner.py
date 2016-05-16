"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import

import copy
import logging
import os

from .. import utils, metric_info


class SonarRunner(object):  # pylint: disable=too-few-public-methods
    """ Class for creating and removing Sonar analyses. """

    def __init__(self, sonar, maven, version_control_system):
        super(SonarRunner, self).__init__()
        self.__sonar = sonar
        self.__maven = maven
        self.__vcs = version_control_system

    def analyse_products(self, products):
        """ Run Sonar on the products and remove old analyses. """
        sonar_analyses_to_keep = set()
        for product in products:
            self.__analyse_product(product)
            sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
            sonar_analyses_to_keep.update(sonar_product_info.all_sonar_ids())
        self.__remove_old_analyses(sonar_analyses_to_keep)

    def __analyse_product(self, product):
        """ Run Sonar on the product, and unit tests if any. """
        product_sonar_id = self.__product_sonar_id(product)
        if not product_sonar_id:
            return
        if not self.__sonar_has_product(product):
            users = ', '.join(['{usr}:{ver}'.format(usr=user.name(), ver=user.product_version() or 'trunk')
                               for user in product.users()])
            logging.info('Check out and run sonar on %s (dependency of %s)', product.product_label(), users or 'none')
            self.__checkout_code_and_run_sonar(product)
        unittests = product.unittests()
        if unittests:
            unittests_sonar_id = self.__product_sonar_id(unittests)
            if unittests_sonar_id != product_sonar_id and not self.__sonar_has_product(unittests):
                # Need to run Sonar again for the unit test coverage:
                self.__checkout_code_and_run_sonar(unittests, unittests=True)
        jsf = product.jsf()
        if jsf and not self.__sonar_has_product(jsf):
            self.__checkout_code_and_run_sonar(jsf)

    def __remove_old_analyses(self, sonar_analyses_to_keep):
        """ Remove Sonar analyses that are no longer needed. """

        def sonar_id_contains_version(sonar_id):
            """ Return whether the Sonar id contains a version number. """
            last_part = sonar_id.split(':')[-1]
            return len(last_part) > 0 and (last_part[0].isdigit() or last_part[-1].isdigit())

        logging.debug('Removing Sonar analyses, keeping %s', sonar_analyses_to_keep)
        for sonar_id in self.__sonar.projects():
            if sonar_id_contains_version(sonar_id) and sonar_id not in sonar_analyses_to_keep and \
               sonar_id.rsplit(':', 1)[0] in sonar_analyses_to_keep:
                self.__sonar.delete_project(sonar_id)

    def __checkout_code_and_run_sonar(self, product, unittests=False):
        """ Check out the product and invoke Sonar through Maven. """
        branch = product.product_branch_id(self.__sonar)
        version = product.product_version()
        folder = product.product_label().replace(':', '_')
        sonar_options = copy.copy(product.metric_source_options(self.__sonar)) or dict()
        sonar_goal = sonar_options.pop('goal', 'sonar:sonar')
        maven_options_string = product.metric_source_options(self.__maven) or ''
        if unittests:
            folder += '-unittests'
            maven_options_string += ' -Dut-coverage=true'
            sonar_branch = 'ut'
            if branch:
                sonar_branch += '_' + branch
            if version:
                sonar_branch += '_' + version
            sonar_options['branch'] = sonar_branch
        else:
            if branch:
                if 'branch' in sonar_options:
                    sonar_options['branch'] += '_' + branch
                else:
                    sonar_options['branch'] = branch
            if version:
                if 'branch' in sonar_options:
                    sonar_options['branch'] += '_' + version
                else:
                    sonar_options['branch'] = version
        sonar_options_string = ' '.join(['-Dsonar.{}={}'.format(*item) for item in sonar_options.items()])
        utils.rmtree(folder)  # Remove any left over checkouts
        self.__check_out(product, folder)
        os.putenv('MAVEN_OPTS', '-Xmx2048m -XX:MaxPermSize=512m')
        maven_command = '{maven} --fail-never clean install {goal} {sopt} {mopt}'.format(
            maven=self.__maven.binary(), goal=sonar_goal, sopt=sonar_options_string, mopt=maven_options_string)
        logging.info(maven_command)
        original_working_dir = os.getcwd()
        try:
            os.chdir(folder)
        except OSError:
            logging.warn("Can't chdir to %s. Check out apparently failed. Skipping Sonar analysis.", folder)
            return
        os.system(maven_command)
        os.chdir(original_working_dir)
        utils.rmtree(folder)  # Remove folder to save space

    def __sonar_has_product(self, product):
        """ Return whether Sonar has an analysis for the product. """
        return self.__sonar.has_project(self.__product_sonar_id(product))

    def __product_sonar_id(self, product):
        """ Return the product's Sonar id. """
        sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
        return sonar_product_info.sonar_id()

    def __check_out(self, product, folder):
        """ Check out the product in the folder. """
        vcs_product_info = metric_info.VersionControlSystemProductInfo(
            self.__vcs if isinstance(self.__vcs, list) else [self.__vcs], product)
        vcs_product_info.vcs().check_out(vcs_product_info.vcs_path(), folder)
