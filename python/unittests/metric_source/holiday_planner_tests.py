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
import datetime
import io
from qualitylib import domain
from qualitylib.metric_source import HolidayPlanner


class HolidayPlannerUnderTest(HolidayPlanner):  # pylint: disable=too-few-public-methods
    """ Override the class under test return static data. """
    def url_open(self, url):  # pylint: disable=unused-argument,no-self-use
        """ Return the static data. """
        next_month = datetime.date.today() + datetime.timedelta(days=30)
        year = next_month.year
        month = next_month.month
        template = u'{{"afwezig":[' \
                        '["3544","desmi","{year}-{month:02d}-12","3"],' \
                        '["3545","desmi","{year}-{month:02d}-13","3"],' \
                        '["3546","desmi","{year}-{month:02d}-14","3"],' \
                        '["3547","desmi","{year}-{month:02d}-15","3"],' \
                        '["3548","desmi","{year}-{month:02d}-16","3"],' \
                        '["3549","desmi","{year}-{month:02d}-17","3"],' \
                        '["3549","desmi","{year}-{month:02d}-18","3"],' \
                        '["3549","desmi","{year}-{month:02d}-19","3"],' \
                        '["3550","piepo","{year}-{month:02d}-11","3"],' \
                        '["3551","piepo","{year}-{month:02d}-12","3"],' \
                        '["3552","piepo","{year}-{month:02d}-13","3"],' \
                        '["3553","piepo","{year}-{month:02d}-14","3"],' \
                        '["3554","piepo","{year}-{month:02d}-15","3"],' \
                        '["3555","piepo","{year}-{month:02d}-16","3"],' \
                        '["3555","piepo","{year}-{month:02d}-17","3"],' \
                        '["3555","piepo","{year}-{month:02d}-18","3"],' \
                        '["3555","piepo","{year}-{month:02d}-19","3"],' \
                        '["3550","alale","{year}-{month:02d}-20","3"],' \
                        '["3550","alale","{year}-{month:02d}-20","3"],' \
                        '["3556","desmi","{year}-{month:02d}-25","3"],' \
                        '["3597","erkat","{year}-{month:02d}-27","3"],' \
                        '["3598","erkat","{year}-{month:02d}-03","3"],' \
                        '["3599","erkat","{year}-{month:02d}-10","3"],' \
                        '["3601","erkat","{year}-{month:02d}-24","3"],' \
                        '["3602","erkat","{year}-{month:02d}-01","3"],' \
                        '["3603","piepo","{year}-{month:02d}-01","3"]'  \
                    ']}}'
        return io.StringIO(template.format(year=year, month=month))


class HolidayPlannerTests(unittest.TestCase):
    """ Unit tests for the holiday planner metric source. """

    def setUp(self):
        self.__planner = HolidayPlannerUnderTest(api_url='http://planner/api')
        self.__team = domain.Team()
        self.__derk = domain.Person('Derk Smikkel', metric_source_ids={self.__planner: 'desmi'})
        self.__team.add_member(self.__derk)
        self.__piet = domain.Person('Piet Poot', metric_source_ids={self.__planner: 'piepo'})
        self.__team.add_member(self.__piet)
        self.__team.add_member(domain.Person('Erwin Kater', metric_source_ids={self.__planner: 'erkat'}))

    def test_value_team_without_members(self):
        """ Test that there is no absence when the team has no members. """
        self.assertEqual((0, None, None, []), self.__planner.days(domain.Team()))

    def test_value_team(self):
        """ Test the absence when the team has members. """
        # Number of days may differ due to how weekends fall.
        self.assertTrue(5 <= self.__planner.days(self.__team)[0] <= 6)

    def test_value_team_members(self):
        """ Test that the absent team members are returned. """
        self.assertEqual(sorted([self.__derk, self.__piet]), sorted(self.__planner.days(self.__team)[3]))

    def test_value_when_no_multiple_team_members_absent(self):
        """ Test that at least two people need to be absent on the same day. """
        team = domain.Team()
        team.add_member(self.__piet)
        team.add_member(domain.Person('No Holiday', metric_source_ids={self.__planner: 'nohol'}))
        self.assertEqual((0, None, None, []), self.__planner.days(team))

    def test_value_when_same_day_listed_multiple_times(self):
        """ Test that listing the same day as holiday multiple times is ignored. """
        team = domain.Team()
        team.add_member(self.__piet)
        team.add_member(domain.Person('Alex Alexander', metric_source_ids={self.__planner: 'alale'}))
        self.assertEqual((0, None, None, []), self.__planner.days(team))
