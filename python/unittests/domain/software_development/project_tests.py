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

import unittest

from qualitylib import domain


class FakeProduct(object):
    """ Fake the product class for unit test purposes. """
    def __init__(self):
        self.__version = None
        self.__branch = None

    @staticmethod
    def name():
        """ Return the name of the product. """
        return 'FakeProduct'

    @staticmethod
    def short_name():
        """ Return the short name of the product. """
        return 'FP'

    def product_version_type(self):
        """ Return the version type of the product. """
        if self.__branch:
            return 'branch'
        elif self.__version:
            return 'tag'
        else:
            return 'trunk'

    def product_version(self):
        """ Return the product version. """
        return self.__version

    def product_branch(self):
        """ Return the product branch. """
        return self.__branch

    def set_product_branch(self, branch):
        """ Set the product branch. """
        self.__branch = branch

    def set_product_version(self, version):
        """ Set the product version. """
        self.__version = version

    @staticmethod
    def dependencies(recursive=False):  # pylint: disable=unused-argument
        """ Return a set of dependent products. """
        return {FakeProduct()}


class ProjectTest(unittest.TestCase):
    """ Test case for the Project domain class. """

    def setUp(self):
        self.__project = domain.Project('Organization', name='Project Name')

    def test_name(self):
        """ Test that the project has the correct name. """
        self.assertEqual('Project Name', self.__project.name())

    def test_organization(self):
        """ Test that the project has the correct organization. """
        self.assertEqual('Organization', self.__project.organization())

    def test_products(self):
        """ Test that a newly created project has no products. """
        self.assertFalse(self.__project.products())

    def test_add_product(self):
        """ Test that a product can be added to the project. """
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertEqual([product], self.__project.products())

    def test_add_product_with_version(self):
        """ Test that a product with a specific version can be added to the project. """
        product = FakeProduct()
        self.__project.add_product(product)
        product1_1 = self.__project.add_product_with_version('FakeProduct', '1.1')
        self.assertEqual([product, product1_1], self.__project.products())

    def test_add_trunk_product(self):
        """ Test that a product without a specific version won't be added to the project. """
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertFalse(self.__project.add_product_with_version('FakeProduct', ''))
        self.assertEqual([product], self.__project.products())

    def test_add_product_with_version_twice(self):
        """ Test that adding a product/version twice is not possible. """
        product = FakeProduct()
        self.__project.add_product(product)
        product1_1 = self.__project.add_product_with_version('FakeProduct', '1.1')
        self.__project.add_product_with_version('FakeProduct', '1.1')
        self.assertEqual([product, product1_1], self.__project.products())

    def test_add_two_products_with_same_abbrev(self):
        """ Test that adding two products with the same abbreviation raises an exception. """
        self.__project.add_product(FakeProduct())
        self.assertRaises(ValueError, self.__project.add_product, FakeProduct())

    def test_add_version_to_missing_product(self):
        """ Test that adding a version for a missing product fails silently. """
        self.__project.add_product(FakeProduct())
        self.__project.add_product_with_version('Missing product', '1.1')

    def test_add_branch_without_branch(self):
        """ Test that a product without a specific branch won't be added to the project. """
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertFalse(self.__project.add_product_with_branch('FakeProduct', ''))
        self.assertEqual([product], self.__project.products())

    def test_add_branch_to_missing_product(self):
        """ Test that adding a branch for a missing product fails silently. """
        self.__project.add_product(FakeProduct())
        self.__project.add_product_with_branch('Missing product', 'branch')

    def test_add_branch(self):
        """ Test that adding a branch for an existing product works. """
        trunk = self.__project.add_product(FakeProduct())
        branch = self.__project.add_product_with_branch('FakeProduct', 'branch')
        self.assertEqual([trunk, branch], self.__project.products())

    def test_add_existing_branch(self):
        """ Test that adding an existing branch does nothing. """
        trunk = self.__project.add_product(FakeProduct())
        branch = self.__project.add_product_with_branch('FakeProduct', 'branch')
        self.assertFalse(self.__project.add_product_with_branch('FakeProduct', 'branch'))
        self.assertEqual([trunk, branch], self.__project.products())

    def test_get_product(self):
        """ Test that an added product can be found. """
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertEqual(product, self.__project.get_product('FakeProduct'))

    def test_get_missing_product(self):
        """ Test that a product that hasn't been added can't be found. """
        self.__project.add_product(FakeProduct())
        self.assertFalse(self.__project.get_product('Missing product'))

    def test_product_dependencies(self):
        """ Test collecting the dependencies of products. """
        self.__project.add_product(FakeProduct())
        self.assertEqual(1, len(self.__project.product_dependencies()))

    def test_teams(self):
        """ Test that a newly created project has no teams. """
        self.assertFalse(self.__project.teams())

    def test_add_team(self):
        """ Test that a team can be added to the project. """
        team = domain.Team()
        self.__project.add_team(team)
        self.assertEqual([team], self.__project.teams())

    def test_dashboard(self):
        """ Test that a dashboard can be set. """
        self.__project.set_dashboard([1, 2], [3, 4])
        self.assertEqual(([1, 2], [3, 4]), self.__project.dashboard())

    def test_add_document(self):
        """ Test that a document can be added to the project. """
        document = domain.Document(name='Title')
        self.__project.add_document(document)
        self.assertTrue(document in self.__project.documents())

    def test_unknown_metric_source(self):
        """ Test that the project returns None for an unknown metric source class. """
        self.assertFalse(self.__project.metric_source(self.__class__))

    def test_known_metric_source(self):
        """ Test that the project returns the instance of a known metric source class. """
        project = domain.Project(metric_sources={''.__class__: 'metric_source'})
        self.assertEqual('metric_source', project.metric_source(''.__class__))

    def test_metric_source_classes(self):
        """ Test that the project returns a list of all metric source classes. """
        project = domain.Project(metric_sources={''.__class__: 'metric_source'})
        self.assertEqual([''.__class__], project.metric_source_classes())

    def test_default_metric_source_classes(self):
        """ Test that the project returns a list of all metric source classes. """
        self.assertEqual([], domain.Project().metric_source_classes())
