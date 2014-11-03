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


class SubversionProductInfo(object):
    ''' Class to represent information that Subversion has about a product. '''
    def __init__(self, subversion, product):
        self.__subversion = subversion
        self.__product = product

    def svn_path(self, version=None, branch=None):
        ''' Return the Subversion path of the product. '''
        version = version or self.__product.product_version()
        branch = branch or self.__product.product_branch_id(self.__subversion)
        old_svn_path = self.__product.old_metric_source_id(self.__subversion,
                                                           version)
        if old_svn_path:
            return old_svn_path
        result = self.__product.metric_source_id(self.__subversion)
        if not result:
            return ''
        result = self.__normalize_path(result)
        if version:
            result = self.__subversion.tags_folder_for_version(result, version)
        elif branch:
            result = self.__subversion.branch_folder_for_branch(result, branch)
        return result

    def latest_released_product_version(self):
        ''' Return the latest released version of the product. '''
        svn_path = self.__product.metric_source_id(self.__subversion)
        if not svn_path:
            return ''
        svn_path = self.__normalize_path(svn_path)
        return self.__subversion.latest_tagged_product_version(svn_path)

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
        return self.__subversion.last_changed_date(self.svn_path())

    @staticmethod
    def __normalize_path(svn_path):
        ''' Return a normalized version of the path. '''
        if not svn_path.endswith('/'):
            svn_path += '/'
        if not '/trunk/' in svn_path:
            svn_path += 'trunk/'
        return svn_path
