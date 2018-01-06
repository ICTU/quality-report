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

from hqlib import domain


class FakeProduct(object):
    """ Fake the product class for unit test purposes. """
    @staticmethod
    def name():
        """ Return the name of the product. """
        return 'FakeProduct'

    @staticmethod
    def short_name():
        """ Return the short name of the product. """
        return 'FP'


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

    def test_add_two_products_with_same_abbrev(self):
        """ Test that adding two products with the same abbreviation raises an exception. """
        self.__project.add_product(FakeProduct())
        self.assertRaises(ValueError, self.__project.add_product, FakeProduct())

    def test_get_product(self):
        """ Test that an added product can be found. """
        product = FakeProduct()
        self.__project.add_product(product)
        self.assertEqual(product, self.__project.get_product('FakeProduct'))

    def test_get_missing_product(self):
        """ Test that a product that hasn't been added can't be found. """
        self.__project.add_product(FakeProduct())
        self.assertFalse(self.__project.get_product('Missing product'))

    def test_teams(self):
        """ Test that a newly created project has no teams. """
        self.assertFalse(self.__project.teams())

    def test_add_team(self):
        """ Test that a team can be added to the project. """
        team = domain.Team()
        self.__project.add_team(team)
        self.assertEqual([team], self.__project.teams())

    def test_add_environment(self):
        """ Test that an environment can be added to the project. """
        environment = domain.Environment()
        self.__project.add_environment(environment)
        self.assertEqual([environment], self.__project.environments())

    def test_dashboard(self):
        """ Test that a dashboard can be set. """
        self.__project.set_dashboard([1, 2], [3, 4])
        self.assertEqual(([1, 2], [3, 4]), self.__project.dashboard())

    def test_add_document(self):
        """ Test that a document can be added to the project. """
        document = domain.Document(name='Title')
        self.__project.add_document(document)
        self.assertTrue(document in self.__project.documents())

    def test_default_domain_object_classes(self):
        """ Test that the project has no domain object classes by default. """
        self.assertEqual(set(), domain.Project().domain_object_classes())

    def test_environment_in_domain_object_classes(self):
        """ Test that the environment class is included in the domain object classes. """
        project = domain.Project()
        project.add_environment(domain.Environment())
        self.assertEqual({domain.Environment}, project.domain_object_classes())

    def test_add_process(self):
        """ Test that a process can be added to the project ."""
        process = domain.Process(name="Scrum")
        self.__project.add_process(process)
        self.assertEqual([process], self.__project.processes())

    def test_get_process(self):
        """ Test that a process can be retrieved by name. """
        process = domain.Process(name="Scrum")
        self.__project.add_process(process)
        self.assertEqual(process, self.__project.get_process(process.name()))

    def test_get_unknown_process(self):
        """ Test getting an unknown process. """
        self.assertEqual(None, self.__project.get_process("Unknown process"))
