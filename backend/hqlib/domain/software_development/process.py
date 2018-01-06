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

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement  # Run time import to prevent circular dependency.
        return (requirement.TrackActions, requirement.TrackRisks,
                requirement.TrackBugs, requirement.TrackSecurityBugs, requirement.TrackStaticSecurityBugs,
                requirement.TrackSecurityTestDate, requirement.TrackQualityGate, requirement.TrackFindings,
                requirement.TrackTechnicalDebt,
                requirement.TrackReadyUS, requirement.TrackSecurityAndPerformanceRisks,
                requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories,
                requirement.TrackManualLTCs)
