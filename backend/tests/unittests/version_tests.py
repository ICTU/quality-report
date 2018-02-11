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

from hqlib import NAME, VERSION


class VersionTest(unittest.TestCase):
    """ Unit tests for the HQ version. """
    def test_name(self):
        """ Test that the name is correct. """
        self.assertEqual("HQ", NAME)

    def test_parts(self):
        """ Test that the version number string consists of three integers. """
        self.assertEqual([int, int, int], [type(int(part)) for part in VERSION.split('.')])
