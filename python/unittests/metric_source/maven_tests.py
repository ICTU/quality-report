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

from qualitylib import metric_source


class MavenTests(unittest.TestCase):
    """ Unit test for the Maven metric source. """
    def test_create(self):
        """ Test that we can create a Maven instance. """
        self.assertTrue(metric_source.Maven())

    def test_default_binary(self):
        """ Test the default binary for Maven. """
        self.assertEqual('mvn', metric_source.Maven().binary())

    def test_specify_binary(self):
        """ Test that the binary can be specified when creating Maven. """
        self.assertEqual('mvn3', metric_source.Maven(binary='mvn3').binary())
