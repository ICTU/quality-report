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

from qualitylib.domain.measurement.measurable import MeasurableObject


class Team(MeasurableObject):
    ''' Class for representing a team. '''

    def __init__(self, short_name=None, is_scrum_team=False,
                 is_support_team=False, release_archives=None,
                 days_per_sprint=21, *args, **kwargs):
        super(Team, self).__init__(*args, **kwargs)
        if short_name:
            assert len(short_name) == 2
        self.__short_name = short_name or self.name()[:2].upper()
        self.__release_archives = release_archives or []
        self.__is_scrum_team = is_scrum_team
        self.__is_support_team = is_support_team
        self.__days_per_sprint = days_per_sprint

    def __eq__(self, other):
        return self.id_string() == other.id_string()

    def __str__(self):
        return self.name()

    def id_string(self):
        ''' Return an id string for the team. '''
        return self.name().lower().replace(' ', '_')

    def short_name(self):
        ''' Return an abbreviation of the team name. '''
        return self.__short_name

    def release_archives(self):
        ''' Return the release archives of the team. '''
        return self.__release_archives

    def is_scrum_team(self):
        ''' Return whether this team is a Scrum team, which means it is
            doing product development. '''
        return self.__is_scrum_team

    def is_support_team(self):
        ''' Return whether this team is a support team, which means it is not
            doing direct product development. '''
        return self.__is_support_team

    def days_per_sprint(self):
        ''' Return the sprint length in days that the team uses. '''
        return self.__days_per_sprint

    def team_resources(self):
        ''' Return the resources of the team. '''
        resources = []
        for release_archive in self.release_archives():
            resources.append(('Release archief team %s' % self.name(), 
                              release_archive.url()))
        return resources
