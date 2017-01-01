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

from hqlib import domain


class RequirementUnderTest(domain.Requirement):  # pylint: disable=too-few-public-methods
    """ Requirement for testing purposes. """
    _name = 'Be user friendly'
    _metric_classes = ['FakeMetricClass 1']


class AddedRequirement(domain.Requirement):  # pylint: disable=too-few-public-methods
    """ A requirement to be added to the default requirements. """
    _name = 'Whatever'
    _metric_classes = ['FakeMetricClass 2']


class RemovedRequirement(domain.Requirement):  # pylint: disable=too-few-public-methods
    """ A requirement to be removed from the defaul requirements. """
    _name = 'Canceled'
    _metric_classes = []


class RequirementTest(unittest.TestCase):
    """ Unit tests for the Requirement domain class. """
    def setUp(self):
        self.__requirement = RequirementUnderTest()

    def test_name(self):
        """ Test the name of the requirement. """
        self.assertEqual('Be user friendly', self.__requirement.name())

    def test_metric_classes(self):
        """ Test that the metric classes can be retrieved. """
        self.assertEqual(['FakeMetricClass 1'], self.__requirement.metric_classes())


class RequirementSubjectUnderTest(domain.software_development.requirement.RequirementSubject):
    # pylint: disable=too-few-public-methods
    """ Override requirement subject to give it default requirement. """
    def __init__(self, default_requirements, optional_requirements, *args, **kwargs):
        self.__default_requirements = default_requirements
        self.__optional_requirements = optional_requirements
        super(RequirementSubjectUnderTest, self).__init__(*args, **kwargs)

    def default_requirements(self):
        """ Return the default requirements for the subject. """
        return self.__default_requirements

    def optional_requirements(self):
        """ Return the optional requirements for the subject. """
        return self.__optional_requirements


class RequirementSubjectTest(unittest.TestCase):
    """ Unit tests for the Requirement Subject domain class. """
    def setUp(self):
        self.__requirement = RequirementUnderTest()
        self.__added = AddedRequirement()
        self.__removed = RemovedRequirement()
        self.__subject = RequirementSubjectUnderTest(
            default_requirements={self.__requirement, self.__removed},
            optional_requirements={self.__added},
            added_requirements=[self.__added],
            removed_requirements=[self.__removed])

    def test_actual_requirements(self):
        """ Test that requirements can be given to a requirement subject. """
        expected = (self.__subject.default_requirements() | {self.__added}) - {self.__removed}
        self.assertEqual(expected, self.__subject.requirements())

    def test_required_metric_classes(self):
        """ Test that the required metric classes are returned based on the requirements. """
        self.assertEqual({'FakeMetricClass 1', 'FakeMetricClass 2'}, self.__subject.required_metric_classes())

    def test_optional_requirements(self):
        """ Test that the default optional requirements are empty. """
        self.assertEqual({self.__added}, self.__subject.optional_requirements())
