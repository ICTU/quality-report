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
from __future__ import absolute_import

from .requirement import RequirementSubject
from ..measurement.measurable import MeasurableObject


class Team(RequirementSubject, MeasurableObject):
    """ Class for representing a team. """

    def __init__(self, short_name=None, *args, **kwargs):
        super(Team, self).__init__(*args, **kwargs)
        if short_name:
            assert len(short_name) == 2
        self.__short_name = short_name or self.name()[:2].upper()
        self.__members = set()

    @staticmethod
    def default_requirements():
        from ... import requirement  # Run time import to prevent circular dependency.
        return {requirement.TrackSpirit}

    @staticmethod
    def optional_requirements():
        from ... import requirement  # Run time import to prevent circular dependency.
        return {requirement.TrackAbsence, requirement.ScrumTeam}

    def __eq__(self, other):
        return self.id_string() == other.id_string()

    def __str__(self):
        return self.name()

    def id_string(self):
        """ Return an id string for the team. """
        return self.name().lower().replace(' ', '_')

    def short_name(self):
        """ Return an abbreviation of the team name. """
        return self.__short_name

    def members(self):
        """ Return the team members. """
        return self.__members

    def add_member(self, person):
        """ Add the person as a team member. """
        self.__members.add(person)
