'''
Copyright 2012-2015 Ministerie van Sociale Zaken en Werkgelegenheid

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


class FakeVersionControlSystem(object):

    metric_source_name = 'FakeVCS'

    ''' Fake a Subversion repository. '''
    def __init__(self, url='', latest_release='1.1', last_changed_date=datetime.datetime(2000, 1, 1)):
        self.__url = url
        self.__latest_release = latest_release
        self.__last_changed_date = last_changed_date

    def latest_tagged_product_version(self, svn_path):
        # pylint: disable=unused-argument
        ''' Return the latest tagged product version from Subversion. '''
        return self.__latest_release

    @staticmethod
    def branch_folder_for_branch(trunk, branch):
        ''' Return the branch folder for the branch. '''
        return metric_source.Subversion.branch_folder_for_branch(trunk, branch)

    def last_changed_date(self, svn_path):  # pylint: disable=unused-argument
        ''' Return the date the path was last changed in Subversion. '''
        return self.__last_changed_date

    def normalize_path(self, svn_path):
        ''' Return the normalized version of the path. '''
        return self.__url + svn_path



class VersionControlSystemProductInfoTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    '''Unit tests for the Subversion product information class. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__subversion = FakeVersionControlSystem()
        self.__project = domain.Project('Organization', name='Project name',
            metric_sources={metric_source.Subversion: self.__subversion})
        self.__product = domain.Product(self.__project,
            metric_source_ids={self.__subversion: 'http://svn/product/trunk/'},
            product_branches={'branch1': {self.__subversion: 'br1'}})
        self.__subversion_product_info = metric_info.VersionControlSystemProductInfo(
            [self.__subversion], self.__product)

    def test_svn_path(self):
        ''' Test that the Subversion path of the product equals the passed
            path. '''
        self.assertEqual('http://svn/product/trunk/',
                         self.__subversion_product_info.vcs_path())

    def test_old_svn_path(self):
        ''' Test that the old Subversion path is returned, if any. '''

        product = domain.Product(self.__project,
            metric_source_ids={self.__subversion: 'http://svn/product/trunk/'},
            old_metric_source_ids={self.__subversion: {'1.1':
                                                       'http://svn/old/'}})

        product.set_product_version('1.1')
        subversion_product_info = metric_info.VersionControlSystemProductInfo( \
            [self.__subversion], product)
        self.assertEqual('http://svn/old/',
                         subversion_product_info.vcs_path())

    def test_svn_path_of_branch(self):
        ''' Test that the subversion path is the branch folder. '''
        self.__product.set_product_branch('branch1')
        subversion_product_info = metric_info.VersionControlSystemProductInfo( \
            [self.__subversion], self.__product)
        self.assertEqual('http://svn/product/branches/br1/',
                         subversion_product_info.vcs_path())

    def test_latest_released_product_version(self):
        ''' Test that the latest release product version is retrieved from
            Subversion. '''
        self.assertEqual('1.1',
            self.__subversion_product_info.latest_released_product_version())

    def test_latest_release_product_version_without_svn_path(self):
        ''' Test that a product without Subversion path doesn't have a latest
            released product version. '''
        subversion_product_info = metric_info.VersionControlSystemProductInfo( \
            [self.__subversion], domain.Product(self.__project))
        self.assertFalse(subversion_product_info.latest_released_product_version())

    def test_is_latest_release(self):
        ''' Test that the product is the latest release if its product version
            is the same as the latest release returned by Subversion. '''
        self.__product.set_product_version('1.1')
        self.assertTrue(self.__subversion_product_info.is_latest_release())

    def test_is_not_lastest_release(self):
        ''' Test that trunk versions are never the latest release. '''
        self.assertFalse(self.__subversion_product_info.is_latest_release())

    def test_last_changed_date(self):
        ''' Test that the date the product was last changed is the date
            reported by Subversion. '''
        self.assertEqual(self.__subversion.last_changed_date('http://svn'),
                         self.__subversion_product_info.last_changed_date())


class MultipleVersionControlSystemProductInfoTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    '''Unit tests for the VersionControlSystemProductInfo class that covers cases of multiple vcs. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__vcs1 = FakeVersionControlSystem('http://svn1/productx/', '1.5', datetime.datetime(2005, 1, 1))
        self.__vcs2 = FakeVersionControlSystem('http://svn2/producty/', '2.0', datetime.datetime(2010, 1, 1))
        self.__vcs_repos=[self.__vcs1, self.__vcs2]
        self.__project = domain.Project('Organization', name='Project name',
            metric_sources={metric_source.Subversion: self.__vcs_repos})

        self.__product1 = domain.Product(self.__project,
            metric_source_ids={self.__vcs1: 'trunk/'},
            old_metric_source_ids={self.__vcs1: {'1.5':'http://svn1/old/'}},
            product_branches={'branch1': {self.__vcs1: 'br1'}})
        self.__product2 = domain.Product(self.__project,
            metric_source_ids={self.__vcs2: 'trunk/'},
            old_metric_source_ids={self.__vcs2: {'2.0':'http://svn2/old/'}},
            product_branches={'branch2': {self.__vcs2: 'br2'}})


    def test_svn_path(self):
        ''' Test that the vcs path of the product equals the passed
            path. '''
        self.__assert_svn_path(self.__product1, 'http://svn1/productx/trunk/')
        self.__assert_svn_path(self.__product2, 'http://svn2/producty/trunk/')

    def test_old_svn_path(self):
        ''' Test that the old vcs path is returned, if any. '''
        self.__assert_old_svn_path(self.__product1, '1.5', 'http://svn1/old/')
        self.__assert_old_svn_path(self.__product2, '2.0', 'http://svn2/old/')

    def test_svn_path_of_branch(self):
        ''' Test that the vcs path is the branch folder. '''
        self.__assert_svn_path_of_branch(self.__product1, 'branch1', 'http://svn1/productx/branches/br1/')
        self.__assert_svn_path_of_branch(self.__product2, 'branch2', 'http://svn2/producty/branches/br2/')

    def test_latest_released_product_version(self):
        ''' Test that the latest release product version is retrieved from vcs. '''
        self.__assert_latest_released_product_version(self.__product1, '1.5')
        self.__assert_latest_released_product_version(self.__product2, '2.0')

    def test_is_latest_release(self):
        ''' Test that the product is the latest release if its product version
            is the same as the latest release returned by vcs. '''
        self.__assert_is_latest_release(self.__product1, '1.5')
        self.__assert_is_latest_release(self.__product2, '2.0')

    def test_is_not_lastest_release(self):
        ''' Test that trunk versions are never the latest release. '''
        self.assertFalse( self.__vcs_prodinfo(self.__product1).is_latest_release())
        self.assertFalse( self.__vcs_prodinfo(self.__product2).is_latest_release())

    def test_last_changed_date(self):
        ''' Test that the date the product was last changed is the date
            reported by vcs. '''
        self.assertEqual(self.__vcs1.last_changed_date('http://svn'),
                          self.__vcs_prodinfo(self.__product1).last_changed_date())
        self.assertEqual(self.__vcs2.last_changed_date('http://svn'),
                          self.__vcs_prodinfo(self.__product2).last_changed_date())



    def __vcs_prodinfo(self, product):
        '''Creates a new VersionControlSystemProductInfo for the given product'''
        return metric_info.VersionControlSystemProductInfo(self.__vcs_repos,product)

    def __assert_svn_path(self, product, expected_path):
        self.assertEqual(expected_path, self.__vcs_prodinfo(product).vcs_path())

    def __assert_old_svn_path(self, product, version_to_set, expected_path):
        product.set_product_version(version_to_set)
        self.__assert_svn_path(product, expected_path)

    def __assert_svn_path_of_branch(self, product, branch_to_set, expected_path):
        product.set_product_branch(branch_to_set)
        self.__assert_svn_path(product, expected_path)

    def __assert_latest_released_product_version(self, product, expected_product_version):
       self.assertEqual(expected_product_version, self.__vcs_prodinfo(product).latest_released_product_version())

    def __assert_is_latest_release(self, product, product_version_to_set):
        product.set_product_version(product_version_to_set)
        self.assertTrue(self.__vcs_prodinfo(product).is_latest_release())