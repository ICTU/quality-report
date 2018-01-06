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


class ProcessTest(unittest.TestCase):
    """ Unit tests for the domain class software development process. """

    def test_name(self):
        """ Test the process name. """
        self.assertEqual('Dev process', domain.Environment('Dev process').name())

    def test_short_name(self):
        """ Test the process short name. """
        self.assertEqual('DP', domain.Environment('Dev process', short_name='DP').short_name())

    def test_default_requirements(self):
        """ Test that a process has no default requirements. """
        self.assertEqual(tuple(), domain.Process().default_requirements())
