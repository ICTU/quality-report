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
from __future__ import absolute_import


class VersionControlSystemProductInfo(object):
    ''' Class to represent information that Subversion has about a product. '''
    def __init__(self, version_control_system, product):
        self.__vcs = version_control_system
        self.__product = product

    def vcs_path(self, version=None, branch=None):
        ''' Return the version control system path of the product. '''
        version = version or self.__product.product_version()
        branch = branch or self.__product.product_branch_id(self.__vcs)
        old_vcs_path = self.__product.old_metric_source_id(self.__vcs, version)
        if old_vcs_path:
            return old_vcs_path
        result = self.__product.metric_source_id(self.__vcs)
        if not result:
            return ''
        result = self.__vcs.normalize_path(result)
        if version:
            result = self.__vcs.tags_folder_for_version(result, version)
        elif branch:
            result = self.__vcs.branch_folder_for_branch(result, branch)
        return result

    def latest_released_product_version(self):
        ''' Return the latest released version of the product. '''
        vcs_path = self.__product.metric_source_id(self.__vcs)
        if not vcs_path:
            return ''
        vcs_path = self.__vcs.normalize_path(vcs_path)
        return self.__vcs.latest_tagged_product_version(vcs_path)

    def is_latest_release(self):
        ''' Return whether the version of the product is the latest 
            released version. '''
        product_version = self.__product.product_version()
        if product_version:
            return product_version == self.latest_released_product_version()
        else:
            return False

    def last_changed_date(self):
        ''' Return the date the product was last changed. '''
        return self.__vcs.last_changed_date(self.vcs_path())
