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


class RequirementTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Unit tests for the Requirement domain class. """
    def setUp(self):  # pylint: disable=C0103
        self.__requirement = domain.Requirement(name='Be user friendly', metric_classes=['Metric'])

    def test_name(self):
        """ Test the name of the requirement. """
        self.assertEqual('Be user friendly', self.__requirement.name())

    def test_metric_classes(self):
        """ Test that the metric classes can be retrieved. """
        self.assertEqual(['Metric'], self.__requirement.metric_classes())
