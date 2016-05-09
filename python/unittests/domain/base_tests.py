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


class DomainObjectTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the base domain object class. """
    def setUp(self):  # pylint: disable=invalid-name
        self.__object = domain.DomainObject(name='Name', url='http://url')

    def test_name(self):
        """ Test the name of the domain object. """
        self.assertEqual('Name', self.__object.name())

    def test_url(self):
        """ Test the url of the domain object. """
        self.assertEqual('http://url', self.__object.url())
