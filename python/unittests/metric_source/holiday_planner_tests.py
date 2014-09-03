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

import unittest
import datetime
import StringIO
from qualitylib import domain
from qualitylib.metric_source import HolidayPlanner


class HolidayPlannerUnderTest(HolidayPlanner):
    def url_open(self, url):
        next_month = datetime.date.today() + datetime.timedelta(days=30)
        year = next_month.year
        month = next_month.month
        return StringIO.StringIO('{"afwezig":[' \
            '["3544","desmi","%(year)d-%(month)02d-12","3"],' \
            '["3545","desmi","%(year)d-%(month)02d-13","3"],' \
            '["3546","desmi","%(year)d-%(month)02d-14","3"],' \
            '["3547","desmi","%(year)d-%(month)02d-15","3"],' \
            '["3548","desmi","%(year)d-%(month)02d-16","3"],' \
            '["3549","desmi","%(year)d-%(month)02d-17","3"],' \
            '["3549","desmi","%(year)d-%(month)02d-18","3"],' \
            '["3549","desmi","%(year)d-%(month)02d-19","3"],' \
            '["3550","piepo","%(year)d-%(month)02d-11","3"],' \
            '["3551","piepo","%(year)d-%(month)02d-12","3"],' \
            '["3552","piepo","%(year)d-%(month)02d-13","3"],' \
            '["3553","piepo","%(year)d-%(month)02d-14","3"],' \
            '["3554","piepo","%(year)d-%(month)02d-15","3"],' \
            '["3555","piepo","%(year)d-%(month)02d-16","3"],' \
            '["3555","piepo","%(year)d-%(month)02d-17","3"],' \
            '["3555","piepo","%(year)d-%(month)02d-18","3"],' \
            '["3555","piepo","%(year)d-%(month)02d-19","3"],' \
            '["3556","desmi","%(year)d-%(month)02d-25","3"],' \
            '["3597","erkat","%(year)d-%(month)02d-27","3"],' \
            '["3598","erkat","%(year)d-%(month)02d-03","3"],' \
            '["3599","erkat","%(year)d-%(month)02d-10","3"],' \
            '["3601","erkat","%(year)d-%(month)02d-24","3"],' \
            '["3602","erkat","%(year)d-%(month)02d-01","3"],' \
            '["3603","piepo","%(year)d-%(month)02d-01","3"]]}' % 
            dict(year=year, month=month))


class HolidayPlannerTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the holiday planner metric source. '''

    def setUp(self):  # pylint: disable=invalid-name
        self.__planner = HolidayPlannerUnderTest(api_url='http://planner/api')
        self.__team = domain.Team()
        self.__team.add_member(domain.Person('Derk Smikkel', 
            metric_source_ids={self.__planner: 'desmi'}))
        self.__team.add_member(domain.Person('Piet Poot', 
            metric_source_ids={self.__planner: 'piepo'}))
        self.__team.add_member(domain.Person('Erwin Kater', 
            metric_source_ids={self.__planner: 'erkat'}))

    def test_value_team_without_members(self):
        ''' Test that there is no absence when the team has no members. '''
        self.assertEqual((0, None, None), self.__planner.days(domain.Team()))

    def test_value_team(self):
        ''' Test the absence when the team has members. '''
        # Number of days may differ due to how weekends fall.
        self.failUnless(5 <= self.__planner.days(self.__team)[0] <= 6)
