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
from qualitylib import metric_source, metric_info, domain


class SonarProductInfoTests(unittest.TestCase):
    '''Unit tests for the Sonar product information class. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__sonar = None
        self.__project = domain.Project('Organization', name='Project name',
            metric_sources={metric_source.Sonar: self.__sonar})
        self.__product = domain.Product(self.__project,
            metric_source_ids={self.__sonar: 'sonar:id'},
            old_metric_source_ids={self.__sonar: {'old.version':
                                                  'old-sonar:id'}})
        self.__sonar_product_info = metric_info.SonarProductInfo(self.__sonar,
                                                                 self.__product)

    def test_all_sonar_ids(self):
        ''' Test that by default all Sonar ids consist of just the product 
            Sonar id. '''
        self.assertEqual(set(['sonar:id']), 
                         self.__sonar_product_info.all_sonar_ids())

    def test_all_sonar_ids_released(self):
        ''' Test that for a released product, the set of all Sonar ids only
            contains the product:version id. '''
        self.__product.set_product_version('1.2.3')
        self.assertEqual(set(['sonar:id:1.2.3']), 
                         self.__sonar_product_info.all_sonar_ids())

    def test_all_sonar_ids_unittests(self):
        ''' Test that for a product with unittests, the Sonar id of the 
            unit tests is included in the set of all Sonar ids. '''
        product = domain.Product(self.__project, 
                                 metric_source_ids={self.__sonar: 'sonar:id'},
                                 unittests=domain.Product(self.__project,
                                     metric_source_ids={self.__sonar:
                                                        'sonar:id:ut'}))
        sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
        self.assertEqual(set(['sonar:id', 'sonar:id:ut']),
                         sonar_product_info.all_sonar_ids())

    def test_all_sonar_ids_jsf(self):
        ''' Test that for a product with jsf, the Sonar id of the jsf project
            is included in the set of all Sonar ids. '''
        product = domain.Product(self.__project, 
            metric_source_ids={self.__sonar: 'sonar:id'},
            jsf=domain.Product(self.__project, 
                metric_source_ids={self.__sonar: 'sonar:id:jsf'}))
        sonar_product_info = metric_info.SonarProductInfo(self.__sonar, product)
        self.assertEqual(set(['sonar:id', 'sonar:id:jsf']), 
                         sonar_product_info.all_sonar_ids())
