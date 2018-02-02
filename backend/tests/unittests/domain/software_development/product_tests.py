"""
Copyright 2012-2018 Ministerie van Sociale Zaken en Werkgelegenheid

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

import unittest

from hqlib import domain, requirement


class ProductTest(unittest.TestCase):
    """ Unit tests for the Product domain class. """

    def setUp(self):
        self.__project = domain.Project('Organization')
        self.__product = domain.Product(name='Product')

    def test_product_name(self):
        """ Test that the name of the product equals given name. """
        self.assertEqual('Product', self.__product.name())

    def test_default_art(self):
        """ Test that products have no automated regression test by default. """
        self.assertFalse(self.__product.art())

    def test_art(self):
        """ Test that the automated regression test can be retrieved. """
        art = domain.Product()
        self.assertEqual(art, domain.Product(art=art).art())

    def test_is_main(self):
        """ Test that the product is part of the main system by default. """
        self.assertTrue(self.__product.is_main())


class ComponentTest(unittest.TestCase):
    """ Unit test for the component class. """

    def test_default_requirements(self):
        """ Test that the default requirements are correct. """
        self.assertEqual((requirement.CodeQuality, requirement.UnitTests, requirement.UnitTestCoverage,
                          requirement.TrackBranches),
                         domain.Component.default_requirements())

    def test_optional_requirements(self):
        """ Test that the optional requirements don't contain the default requirements. """
        self.assertFalse(set(domain.Component.default_requirements()) & set(domain.Component.optional_requirements()))


class ApplicationTest(unittest.TestCase):
    """ Unit test for the application class. """

    def test_default_requirements(self):
        """ Test that the default requirements are correct. """
        self.assertEqual((requirement.CodeQuality, requirement.ART, requirement.ARTCoverage, requirement.TrackBranches,
                          requirement.PerformanceLoad, requirement.PerformanceEndurance,
                          requirement.OWASPDependencies, requirement.OWASPZAP, requirement.Checkmarx),
                         domain.Application.default_requirements())

    def test_optional_requirements(self):
        """ Test that the optional requirements don't contain the default requirements. """
        self.assertFalse(set(domain.Application.default_requirements()) &
                         set(domain.Application.optional_requirements()))
