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

import unittest
import datetime
from qualitylib import metric_source, metric_info, domain


class FakeSubversion(object):
    ''' Fake a Subversion repository. '''
    @staticmethod
    def latest_tagged_product_version(svn_path):  
        # pylint: disable=unused-argument
        ''' Return the latest tagged product version from Subversion. '''
        return '1.1'

    @staticmethod
    def branch_folder_for_branch(trunk, branch):
        ''' Return the branch folder for the branch. '''
        return metric_source.Subversion.branch_folder_for_branch(trunk, branch)

    @staticmethod
    def last_changed_date(svn_path):  # pylint: disable=unused-argument
        ''' Return the date the path was last changed in Subversion. '''
        return datetime.datetime(2000, 1, 1)


class SubversionProductInfoTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    '''Unit tests for the Subversion product information class. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = FakeSubversion()
        self.__project = domain.Project('Organization', name='Project name',
            metric_sources={metric_source.Subversion: self.__subversion})
        self.__product = domain.Product(self.__project,
            metric_source_ids={self.__subversion: 'http://svn/product/trunk/'},
            product_branches={'branch1': {self.__subversion: 'br1'}})
        self.__subversion_product_info = metric_info.SubversionProductInfo( \
            self.__subversion, self.__product)

    def test_svn_path(self):
        ''' Test that the Subversion path of the product equals the passed 
            path. '''
        self.assertEqual('http://svn/product/trunk/',
                         self.__subversion_product_info.svn_path())

    def test_old_svn_path(self):
        ''' Test that the old Subversion path is returned, if any. '''
        product = domain.Product(self.__project,
            old_metric_source_ids={self.__subversion: {'1.1':
                                                       'http://svn/old/'}})
        product.set_product_version('1.1')
        subversion_product_info = metric_info.SubversionProductInfo( \
            self.__subversion, product)
        self.assertEqual('http://svn/old/',
                         subversion_product_info.svn_path())

    def test_svn_path_of_branch(self):
        ''' Test that the subversion path is the branch folder. '''
        self.__product.set_product_branch('branch1')
        subversion_product_info = metric_info.SubversionProductInfo( \
            self.__subversion, self.__product)
        self.assertEqual('http://svn/product/branches/br1/', 
                         subversion_product_info.svn_path())

    def test_latest_released_product_version(self):
        ''' Test that the latest release product version is retrieved from
            Subversion. '''
        self.assertEqual('1.1', 
            self.__subversion_product_info.latest_released_product_version())

    def test_latest_release_product_version_without_svn_path(self):
        ''' Test that a product without Subversion path doesn't have a latest
            released product version. '''
        subversion_product_info = metric_info.SubversionProductInfo( \
            self.__subversion, domain.Product(self.__project))
        self.failIf(subversion_product_info.latest_released_product_version())

    def test_is_latest_release(self):
        ''' Test that the product is the latest release if its product version
            is the same as the latest release returned by Subversion. '''
        self.__product.set_product_version('1.1')
        self.failUnless(self.__subversion_product_info.is_latest_release())

    def test_is_not_lastest_release(self):
        ''' Test that trunk versions are never the latest release. '''
        self.failIf(self.__subversion_product_info.is_latest_release())

    def test_last_changed_date(self):
        ''' Test that the date the product was last changed is the date
            reported by Subversion. '''
        self.assertEqual(self.__subversion.last_changed_date('http://svn'),
                         self.__subversion_product_info.last_changed_date())
