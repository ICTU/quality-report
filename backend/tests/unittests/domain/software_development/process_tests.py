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

from hqlib import domain, requirement


class ProcessTest(unittest.TestCase):
    """ Unit tests for the domain class software development process. """

    def test_default_requirements(self):
        """ Test that a process has no default requirements. """
        self.assertEqual(tuple(), domain.Process.default_requirements())

    def test_optional_requirements(self):
        """ Test that a process has optional requirements. """
        self.assertTrue(domain.Process.optional_requirements())

    def test_process_types_cover_process(self):
        """ Test that the set of process requirements equals the union of the requirements of the process types. """

        def all_requirements(*domain_classes):
            """ Return all requirements of the domain class. """
            result = set()
            for domain_class in domain_classes:
                result |= set(domain_class.default_requirements()) | set(domain_class.optional_requirements())
            return result

        self.assertEqual(all_requirements(domain.Process),
                         all_requirements(domain.ProjectManagement, domain.IssueManagement,
                                          domain.Scrum) | {requirement.TrackQualityGate})

    def test_default_name(self):
        """ Test that the process has a default name. """
        self.assertEqual("Process", domain.Process().name())

    def test_name_can_be_overridden(self):
        """ Test that the process name can be overridden. """
        self.assertEqual("Development process", domain.Process(name="Development process").name())

    def test_default_short_name(self):
        """ Test that the process has a default short name. """
        self.assertEqual("PP", domain.Process().short_name())

    def test_short_name_can_be_overridden(self):
        """ Test that the process short name can be overridden. """
        self.assertEqual("ZZ", domain.Process(short_name="ZZ").short_name())


class ProjectManagementTest(unittest.TestCase):
    """ Unit tests for the project management domain class. """
    def test_default_requirements(self):
        """ Test that the default requirements are correct. """
        self.assertEqual((requirement.TrackActions, requirement.TrackRisks),
                         domain.ProjectManagement.default_requirements())

    def test_optional_requirements(self):
        """ Test that the optional requirements are correct. """
        self.assertEqual((requirement.TrackSecurityTestDate,), domain.ProjectManagement.optional_requirements())

    def test_default_name(self):
        """ Test that the process has a default name. """
        self.assertEqual("Project management", domain.ProjectManagement().name())

    def test_default_short_name(self):
        """ Test that the process has a default short name. """
        self.assertEqual("PM", domain.ProjectManagement().short_name())


class IssueManagementTest(unittest.TestCase):
    """ Unit tests for the issue management domain class. """
    def test_default_requirements(self):
        """ Test that the default requirements are correct. """
        self.assertEqual((requirement.TrackBugs,), domain.IssueManagement.default_requirements())

    def test_optional_requirements(self):
        """ Test that the optional requirements are correct. """
        self.assertEqual((requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
                          requirement.TrackFindings, requirement.TrackTechnicalDebt),
                         domain.IssueManagement.optional_requirements())

    def test_default_name(self):
        """ Test that the process has a default name. """
        self.assertEqual("Issue management", domain.IssueManagement().name())

    def test_default_short_name(self):
        """ Test that the process has a default short name. """
        self.assertEqual("IM", domain.IssueManagement().short_name())


class ScrumTest(unittest.TestCase):
    """ Unit tests for the Scrum domain class. """
    def test_default_requirements(self):
        """ Test that the default requirements are correct. """
        self.assertEqual((requirement.UserStoriesAndLTCs, requirement.TrackReadyUS,
                          requirement.TrackSecurityAndPerformanceRisks, requirement.TrackManualLTCs),
                         domain.Scrum.default_requirements())

    def test_optional_requirements(self):
        """ Test that the optional requirements are correct. """
        self.assertEqual((requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories,
                          requirement.PredictUserStories),
                         domain.Scrum.optional_requirements())

    def test_default_name(self):
        """ Test that the process has a default name. """
        self.assertEqual("Scrum", domain.Scrum().name())

    def test_default_short_name(self):
        """ Test that the process has a default short name. """
        self.assertEqual("SC", domain.Scrum().short_name())
