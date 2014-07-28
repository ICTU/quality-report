'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import domain
import unittest


class TeamTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    ''' Unit tests for the Team domain class. '''
    def setUp(self):  # pylint: disable=C0103
        self.__team = domain.Team(name='The A-team')

    def test_default_scrum_team(self):
        ''' Test that a team is not a Scrum team by default. '''
        self.failIf(self.__team.is_scrum_team())

    def test_default_support_team(self):
        ''' Test that a team is not a support team by default. '''
        self.failIf(self.__team.is_support_team())

    def test_default_release_archives(self):
        ''' Test that a team has no release archives by default. '''
        self.failIf(self.__team.release_archives())

    def test_one_release_archive(self):
        ''' Test giving a team release archives. '''
        team = domain.Team(name='The B-team',
                           release_archives=['Release archive'])
        self.assertEqual(['Release archive'], team.release_archives())

    def test_id_string(self):
        ''' Test that the id string is the team name as identifier. '''
        self.assertEqual('the_a-team', self.__team.id_string())

    def test_default_short_name(self):
        ''' Test that the default short name of the team equals the first two
            letters of the team name. '''
        self.assertEqual('TH', self.__team.short_name())

    def test_short_name(self):
        ''' Test that the short name of the team can also be passed at 
            initialization. '''
        self.assertEqual('ZZ', domain.Team(name='ABC', 
                                           short_name='ZZ').short_name())

    def test_str(self):
        ''' Test that the string formatting of a team equals the team name. '''
        self.assertEqual(self.__team.name(), str(self.__team))

    def test_default_sprint_length(self):
        ''' Test the default sprint length of the team. '''
        self.assertEqual(21, self.__team.days_per_sprint())
