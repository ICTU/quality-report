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


import datetime
import logging
from typing import Dict, List, Optional

from .. import domain, metric_source
from hqlib.typing import DateTime


class VersionControlSystemProductInfo(object):
    """ Class to represent information that the version control system has about a product. """
    def __init__(self, version_control_system: List[metric_source.VersionControlSystem],
                 product: domain.Product) -> None:
        self.__vcs = self.__find_repo(version_control_system, product)
        self.__product = product
        self.metric_source_name = self.__vcs.metric_source_name if self.__vcs else 'VCS not configured'

    def vcs_path(self) -> str:
        """ Return the version control system path of the product. """
        if not self.__vcs:
            return ''
        result = self.__product.metric_source_id(self.__vcs)
        return self.__vcs.normalize_path(result) if result else ''

    def branch_folder_for_branch(self, path: str, branch: str) -> str:
        """ Return the folder for the branch. """
        return self.__vcs.branch_folder_for_branch(path, branch) if self.__vcs else ''

    def last_changed_date(self, path: str=None) -> DateTime:
        """ Return the date the path was last changed. """
        return self.__vcs.last_changed_date(path or self.vcs_path()) if self.__vcs else datetime.datetime.min

    def unmerged_branches(self, path: str, list_of_branches_to_ignore: List[str]=None, re_of_branches_to_ignore: str='',
                          list_of_branches_to_include: List[str]=None) -> Dict[str, int]:
        """ Return a list of branches that haven't been merged with the trunk. """
        return self.__vcs.unmerged_branches(path, list_of_branches_to_ignore, re_of_branches_to_ignore,
                                            list_of_branches_to_include) if self.__vcs else dict()

    def branches(self, path: str) -> List[str]:
        """ Return a list of branches. """
        return self.__vcs.branches(path) if self.__vcs else []

    @staticmethod
    def __find_repo(vcs: List[metric_source.VersionControlSystem],
                    product: domain.Product) -> Optional[metric_source.VersionControlSystem]:
        """ Loops through all VCS instances when vcs is a list and returns the instance linked to the product.
            If vcs is not a list but a single instance, that instance is returned.
            If the product is None, None is returned. """
        if product:
            try:
                return [repo for repo in vcs if product.metric_source_id(repo)][0]
            except IndexError:
                logging.warning('There is no VCS configured for %s',
                                product.name() if hasattr(product, 'name') else product)
        return None
