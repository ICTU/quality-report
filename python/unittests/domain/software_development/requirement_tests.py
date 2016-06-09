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
    """ Unit tests for the Requirement domain class. """
    def setUp(self):
        self.__requirement = domain.Requirement(name='Be user friendly', metric_classes=['FakeMetricClass'])

    def test_name(self):
        """ Test the name of the requirement. """
        self.assertEqual('Be user friendly', self.__requirement.name())

    def test_metric_classes(self):
        """ Test that the metric classes can be retrieved. """
        self.assertEqual(['FakeMetricClass'], self.__requirement.metric_classes())


class RequirementSubjectTest(unittest.TestCase):
    """ Unit tests for the Requirement Subject domain class. """
    def setUp(self):
        self.__requirement = domain.Requirement('A requirement', metric_classes=['FakeMetricClass'])
        self.__subject = domain.software_development.requirement.RequirementSubject(requirements=[self.__requirement])

    def test_requirements(self):
        """ Test that requirements can be given to a requirement subject. """
        self.assertTrue(self.__requirement in self.__subject.requirements())

    def test_required_metric_classes(self):
        """ Test that the required metric classes are returned based on the requirements. """
        self.assertTrue('FakeMetricClass' in self.__subject.required_metric_classes())
