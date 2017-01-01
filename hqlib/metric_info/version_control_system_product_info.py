"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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

import datetime
import logging

from .. import domain


class VersionControlSystemProductInfo(object):
    """ Class to represent information that the version control system has about a product. """
    def __init__(self, version_control_system, product):
        self.__vcs = self.__find_repo(version_control_system, product)
        self.__product = product
        self.metric_source_name = self.__vcs.metric_source_name if self.__vcs else 'VCS not configured'

    def vcs(self):
        """ Return the version control system where the product lives. """
        return self.__vcs

    def vcs_path(self, version=None):
        """ Return the version control system path of the product. """
        old_vcs_path = self.__product.old_metric_source_id(self.__vcs, version)
        if old_vcs_path:
            return old_vcs_path
        result = self.__product.metric_source_id(self.__vcs)
        if not result:
            return ''
        result = self.__vcs.normalize_path(result)
        if version:
            result = self.__vcs.tags_folder_for_version(result, version)
        return result

    def branch_folder_for_branch(self, path, branch):
        """ Return the folder for the branch. """
        return self.__vcs.branch_folder_for_branch(path, branch)

    def last_changed_date(self, path=None):
        """ Return the date the path was last changed. """
        return datetime.datetime.min if self.__vcs is None else self.__vcs.last_changed_date(path or self.vcs_path())

    def unmerged_branches(self, path, list_of_branches_to_ignore=None, re_of_branches_to_ignore='',
                          list_of_branches_to_include=None):
        """ Return a list of branches that haven't been merged with the trunk. """
        return self.__vcs.unmerged_branches(path, list_of_branches_to_ignore, re_of_branches_to_ignore,
                                            list_of_branches_to_include)

    def branches(self, path):
        """ Return a list of branches. """
        return self.__vcs.branches(path)

    @staticmethod
    def __find_repo(vcs, product):
        """ Loops through all VCS instances when vcs is a list and returns the instance linked to the product.
            If vcs is not a list but a single instance, that instance is returned.
            If the product is None, None is returned. """
        if product:
            try:
                return [repo for repo in vcs if product.metric_source_id(repo)][0]
            except IndexError:
                logging.warning('There is no VCS configured for %s',
                                product.name() if hasattr(product, 'name') else product)
        return domain.MissingMetricSource()
