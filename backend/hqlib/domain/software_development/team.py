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

from typing import Set, Sequence, Type

from .requirement import Requirement, RequirementSubject
from ..measurement.measurable import MeasurableObject
from .person import Person


class Team(RequirementSubject, MeasurableObject):
    """ Class for representing a team. """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__members: Set[Person] = set()

    @staticmethod
    def default_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement  # Run time import to prevent circular dependency.
        return requirement.TrackSpirit,

    @staticmethod
    def optional_requirements() -> Sequence[Type[Requirement]]:
        from ... import requirement  # Run time import to prevent circular dependency.
        return (requirement.TrackAbsence, requirement.TrackUserStoriesInProgress,
                requirement.TrackDurationOfUserStories)

    def __str__(self) -> str:
        return self.name()

    def id_string(self) -> str:
        """ Return an id string for the team. """
        return self.name().lower().replace(' ', '_')

    def members(self) -> Set[Person]:
        """ Return the team members. """
        return self.__members

    def add_member(self, person: Person) -> None:
        """ Add the person as a team member. """
        self.__members.add(person)
