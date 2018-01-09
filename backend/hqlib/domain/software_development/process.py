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

from typing import Sequence, Type

from .requirement import RequirementSubject, Requirement
from ..measurement.measurable import MeasurableObject


class Process(RequirementSubject, MeasurableObject):
    """ Class representing a software development process. """
    default_name = "Process"
    default_short_name = "PP"

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement  # Run time import to prevent circular dependency.
        return (requirement.TrackActions, requirement.TrackRisks,
                requirement.TrackBugs, requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
                requirement.TrackSecurityTestDate, requirement.TrackQualityGate, requirement.TrackFindings,
                requirement.TrackTechnicalDebt,
                requirement.UserStoriesAndLTCs, requirement.TrackReadyUS, requirement.TrackSecurityAndPerformanceRisks,
                requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories,
                requirement.TrackManualLTCs)


class ProjectManagement(Process):
    """ Class representing a project management process. """
    default_name = "Project management"
    default_short_name = "PM"

    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return requirement.TrackActions, requirement.TrackRisks

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return requirement.TrackSecurityTestDate,


class IssueManagement(Process):
    """ Class representing an issue management process. """
    default_name = "Issue management"
    default_short_name = "IM"

    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return requirement.TrackBugs,

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return (requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs, requirement.TrackFindings,
                requirement.TrackTechnicalDebt)


class Scrum(Process):
    """ Class representing a Scrum process. """
    default_name = "Scrum"
    default_short_name = "SC"

    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return (requirement.UserStoriesAndLTCs, requirement.TrackReadyUS, requirement.TrackSecurityAndPerformanceRisks,
                requirement.TrackManualLTCs)

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement
        return requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories
