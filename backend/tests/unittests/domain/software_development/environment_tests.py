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

from hqlib import domain, requirement


class EnvironmentTest(unittest.TestCase):
    """ Unit tests for the domain class software development environment. """

    def test_name(self):
        """ Test the environment name. """
        self.assertEqual('Dev environment', domain.Environment('Dev environment').name())

    def test_short_name(self):
        """ Test the environment short name. """
        self.assertEqual('AC', domain.Environment('Acceptance environment', short_name='AC').short_name())

    def test_default_requirements(self):
        """ Test that an environment can be created. """
        self.assertEqual({requirement.TrackSonarVersion, requirement.TrackCIJobs},
                         domain.Environment().default_requirements())
