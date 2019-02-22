"""
Copyright 2012-2019 Ministerie van Sociale Zaken en Werkgelegenheid

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

from hqlib.domain import DomainObject


class DomainObjectTest(unittest.TestCase):
    """ Unit tests for the base domain object class. """
    def setUp(self):
        self.__object = DomainObject(name='Name', short_name='AC', url='http://url')

    def test_name(self):
        """ Test the name of the domain object. """
        self.assertEqual('Name', self.__object.name())

    def test_short_name(self):
        """ Test the measurable short name. """
        self.assertEqual('AC', self.__object.short_name())

    def test_short_name_with_spaces(self):
        """ Test that the short name isn't allowed to contain spaces. """
        self.assertRaises(ValueError, DomainObject, name="Name", short_name="S p a c e s")

    def test_url(self):
        """ Test the url of the domain object. """
        self.assertEqual('http://url/', self.__object.url())

    def test_compare(self):
        """ Test that domain objects can be compared and sorted. """
        self.assertEqual(DomainObject(name="Name"), DomainObject(name="Name"))
        self.assertNotEqual(DomainObject(name="Name"), DomainObject(name="Other name"))
        self.assertEqual(DomainObject(name="Name", short_name="N"), DomainObject(name="Name", short_name="N"))
        self.assertNotEqual(DomainObject(name="Name", short_name="X"), DomainObject(name="Name", short_name="Y"))
        self.assertEqual(DomainObject(name="Name", url="http://a"), DomainObject(name="Name", url="http://a"))
        self.assertNotEqual(DomainObject(name="Name", url="http://a"), DomainObject(name="Name", url="http://b"))
        self.assertTrue(DomainObject(name="AAA") < DomainObject(name="BBB"))
