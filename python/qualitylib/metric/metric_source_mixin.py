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


# pylint: disable=R0903

class SonarMetricMixin(object):
    ''' Mixin class for metrics that use Sonar. '''
    def __init__(self, *args, **kwargs):
        self._sonar = kwargs.pop('sonar')
        super(SonarMetricMixin, self).__init__(*args, **kwargs)

    def url(self):
        ''' Return the url to Sonar. '''
        return dict(Sonar=self._sonar_url())
    
    def _sonar_url(self):
        ''' Return the Sonar url to use for the metric url. '''
        return self._sonar.url()
    
    def _sonar_id(self):
        ''' Return the id of the subject in Sonar. '''
        return self._subject.sonar_id()


class SonarDashboardMetricMixin(SonarMetricMixin):
    ''' Mixin class for metrics that use the Sonar dashboard. '''
    def _sonar_url(self):
        ''' Return the url to the Sonar dashboard. '''
        return self._sonar.dashboard_url(self._sonar_id())


class SonarViolationsMetricMixin(SonarMetricMixin):
    ''' Mixin class for metrics that use the Sonar violations. '''
    def _sonar_url(self):
        ''' Return the url to the Sonar violations. '''
        return self._sonar.violations_url(self._sonar_id())


class JenkinsMetricMixin(object):
    ''' Mixin class for metrics that use Jenkins. '''
    def __init__(self, *args, **kwargs):
        self._jenkins = kwargs.pop('jenkins')
        super(JenkinsMetricMixin, self).__init__(*args, **kwargs)
        

class BirtMetricMixin(object):
    ''' Mixin class for metrics that use Birt. '''
    def __init__(self, *args, **kwargs):
        self._birt = kwargs.pop('birt')
        super(BirtMetricMixin, self).__init__(*args, **kwargs)

    def _birt_id(self):
        ''' Return the id of the subject in Birt. '''
        return self._subject.birt_id()

        
class BirtTestDesignMetricMixin(BirtMetricMixin):
    ''' Mixin class for metrics that use the Birt test design report. '''
    def url(self):
        ''' Return the url for the What's Missing report instead of the 
            Birt test design report since the What's Missing report allows
            users to click to the user stories and test cases in Jira. '''
        return dict(Birt=self._birt.whats_missing_url(self._birt_id()))


class NagiosMetricMixin(object):
    ''' Mixin class for metrics that use Nagios. '''
    def __init__(self, *args, **kwargs):
        self._nagios = kwargs.pop('nagios')
        super(NagiosMetricMixin, self).__init__(*args, **kwargs)
        

class TrelloActionsBoardMetricMixin(object):
    ''' Mixin class for metrics that use Trello for an actions board. '''
    def __init__(self, *args, **kwargs):
        self._trello_actions_board = kwargs.pop('trello_actions_board')
        super(TrelloActionsBoardMetricMixin, self).__init__(*args, **kwargs)


class JiraMetricMixin(object):
    ''' Mixin class for metrics that use Jira. '''
    def __init__(self, *args, **kwargs):
        self._jira = kwargs.pop('jira')
        super(JiraMetricMixin, self).__init__(*args, **kwargs)


class SubversionMetricMixin(object):
    ''' Mixin class for metrics that use Subversion. '''
    def __init__(self, *args, **kwargs):
        self._subversion = kwargs.pop('subversion')
        super(SubversionMetricMixin, self).__init__(*args, **kwargs)
