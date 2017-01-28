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

import unittest

from hqlib.metric_source import VersionControlSystem


class VersionControlSystemTests(unittest.TestCase):
    """ Unit tests for the version control system class. """

    def assert_version(self, expected_tuple, version_string, expected_string=None):
        """ Helper function to test the parse version method. """
        expected_string = version_string if expected_string is None else expected_string
        self.assertEqual((expected_tuple, expected_string), VersionControlSystem._parse_version(version_string))

    def test_parse_version_empty_tag(self):
        """ Test empty tag. """
        self.assert_version((0, 0, 0), '')

    def test_parse_version_single_digit(self):
        """ Test single digit. """
        self.assert_version((0, 0, 0), '1', expected_string='')

    def test_parse_version_two_digits(self):
        """ Test that x.y works. """
        self.assert_version((1, 2), '1.2')

    def test_parse_version_three_digits(self):
        """ Test that x.y.z works. """
        self.assert_version((1, 2, 3), '1.2.3')

    def test_parse_version_four_digits(self):
        """ Test that x.y.z.a works. """
        self.assert_version((1, 2, 3, 4), '1.2.3.4')

    def test_parse_version_postfix(self):
        """ Test that x.y.z-foo works. """
        self.assert_version((1, 2, 3), '1.2.3-foo')
