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

from hqlib import domain


class TeamTest(unittest.TestCase):
    """ Unit tests for the Team domain class. """
    def setUp(self):
        self.__team = domain.Team(name='The A-team')

    def test_id_string(self):
        """ Test that the id string is the team name as identifier. """
        self.assertEqual('the_a-team', self.__team.id_string())

    def test_eq(self):
        """ Test that teams are equal when their names are. """
        self.assertEqual(self.__team, domain.Team(name='The A-team'))

    def test_no_default_short_name(self):
        """ Test that the team has a default short name. """
        self.assertEqual('NN', self.__team.short_name())

    def test_short_name(self):
        """ Test that the short name of the team can also be passed at initialization. """
        team = domain.Team(name='ABC', short_name='ZZ')
        self.assertEqual('ZZ', team.short_name())

    def test_str(self):
        """ Test that the string formatting of a team equals the team name. """
        self.assertEqual(self.__team.name(), str(self.__team))

    def test_default_team_members(self):
        """ Test that the team has no team members by default. """
        self.assertFalse(self.__team.members())

    def test_add_team_member(self):
        """ Test that a person can be added as team member. """
        piet = domain.Person(name='Piet Programmer')
        self.__team.add_member(piet)
        self.assertTrue(piet in self.__team.members())
