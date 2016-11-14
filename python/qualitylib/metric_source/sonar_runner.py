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

import logging

from .. import metric_info


class SonarRunner(object):  # pylint: disable=too-few-public-methods
    """ Class for removing Sonar analyses. """

    def __init__(self, sonar):
        super(SonarRunner, self).__init__()
        self.__sonar = sonar

    def analyse_products(self, products):
        """ Run Sonar on the products and remove old analyses. """
        sonar_analyses_to_keep = set()
        for product in products:
            sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
            sonar_analyses_to_keep.update(sonar_product_info.all_sonar_ids())
        self.__remove_old_analyses(sonar_analyses_to_keep)

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
