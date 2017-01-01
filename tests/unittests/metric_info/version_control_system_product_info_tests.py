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
import unittest

from hqlib import metric_source, metric_info, domain


class FakeVersionControlSystem(object):
    """ Fake a Subversion repository. """

    metric_source_name = 'FakeVCS'

    def __init__(self, url='', latest_release='1.1', last_changed_date=datetime.datetime(2000, 1, 1)):
        self.__url = url
        self.__latest_release = latest_release
        self.__last_changed_date = last_changed_date

    def last_changed_date(self, svn_path):  # pylint: disable=unused-argument
        """ Return the date the path was last changed in Subversion. """
        return self.__last_changed_date

    def normalize_path(self, svn_path):
        """ Return the normalized version of the path. """
        return self.__url + svn_path


class VersionControlSystemProductInfoTests(unittest.TestCase):
    """t tests for the Subversion product information class. """
    def setUp(self):
        self.__subversion = FakeVersionControlSystem()
        self.__project = domain.Project('Organization', name='Project name',
                                        metric_sources={metric_source.Subversion: self.__subversion})
        self.__product = domain.Product(self.__project,
                                        metric_source_ids={self.__subversion: 'http://svn/product/trunk/'})
        self.__subversion_product_info = metric_info.VersionControlSystemProductInfo([self.__subversion],
                                                                                     self.__product)

    def test_vcs(self):
        """ Test the the vcs can be retrieved. """
        self.assertEqual(self.__subversion, self.__subversion_product_info.vcs())

    def test_svn_path(self):
        """ Test that the Subversion path of the product equals the passed path. """
        self.assertEqual('http://svn/product/trunk/', self.__subversion_product_info.vcs_path())

    def test_last_changed_date(self):
        """ Test that the date the product was last changed is the date reported by Subversion. """
        self.assertEqual(self.__subversion.last_changed_date('http://svn'),
                         self.__subversion_product_info.last_changed_date())


class MultipleVersionControlSystemProductInfoTests(unittest.TestCase):
    """ Unit tests for the VersionControlSystemProductInfo class that covers cases of multiple vcs. """
    def setUp(self):
        self.__vcs1 = FakeVersionControlSystem('http://svn1/productx/', '1.5', datetime.datetime(2005, 1, 1))
        self.__vcs2 = FakeVersionControlSystem('http://svn2/producty/', '2.0', datetime.datetime(2010, 1, 1))
        self.__vcs_repos = [self.__vcs1, self.__vcs2]
        self.__project = domain.Project('Organization', name='Project name',
                                        metric_sources={metric_source.Subversion: self.__vcs_repos})
        self.__product1 = domain.Product(self.__project, metric_source_ids={self.__vcs1: 'trunk/'})
        self.__product2 = domain.Product(self.__project, metric_source_ids={self.__vcs2: 'trunk/'})

    def test_svn_path(self):
        """ Test that the vcs path of the product equals the passed path. """
        self.__assert_svn_path(self.__product1, 'http://svn1/productx/trunk/')
        self.__assert_svn_path(self.__product2, 'http://svn2/producty/trunk/')

    def test_last_changed_date(self):
        """ Test that the date the product was last changed is the date reported by vcs. """
        self.assertEqual(self.__vcs1.last_changed_date('http://svn'),
                         self.__vcs_prodinfo(self.__product1).last_changed_date())
        self.assertEqual(self.__vcs2.last_changed_date('http://svn'),
                         self.__vcs_prodinfo(self.__product2).last_changed_date())

    # Helpers

    def __vcs_prodinfo(self, product):
        """ Creates a new VersionControlSystemProductInfo for the given product. """
        return metric_info.VersionControlSystemProductInfo(self.__vcs_repos, product)

    def __assert_svn_path(self, product, expected_path):
        self.assertEqual(expected_path, self.__vcs_prodinfo(product).vcs_path())
