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


class QualityAttributeTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the quality attribute domain class. """

    def test_id_string(self):
        """ Test that the id string is correct. """
        self.assertEqual('id', domain.QualityAttribute('id').id_string())

    def test_valid(self):
        """ Test that the attribute is True when casted to boolean. """
        self.assertTrue(domain.QualityAttribute('id'))

    def test_not_valid(self):
        """ Test that the attribute is False when it doesn't have a id string. """
        self.assertFalse(domain.QualityAttribute(''))

    def test_equality(self):
        """ Test that two quality attributes are equal when their id strings are equal. """
        self.assertEqual(domain.QualityAttribute('a', name='A'), domain.QualityAttribute('a', name='B'))

    def test_sort(self):
        """ Test that quality attributes are sorted by id string. """
        self.assertTrue(domain.QualityAttribute('a', name='B') < domain.QualityAttribute('b', name='A'))
