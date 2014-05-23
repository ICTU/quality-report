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

# CI: Continuous integration metrics.

from qualitylib.domain import Metric, LowerIsBetterMetric, \
    HigherPercentageIsBetterMetric
from qualitylib.metric.metric_source_mixin import JenkinsMetricMixin
from qualitylib.metric.quality_attributes import ENVIRONMENT_QUALITY, \
    TEST_QUALITY


class ARTStability(JenkinsMetricMixin, Metric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the stability of an ART. An ART is considered to
        be unstable if it hasn't succeeded for multiple days. '''

    name = 'Stabiliteit van automatische regressietest'
    norm_template = 'Alle regressietesten en integratietesten hebben de ' \
        'laatste %(target)d dagen minimaal eenmaal succesvol gedraaid. Rood ' \
        'als er testen meer dan %(low_target)d dagen niet succesvol ' \
        'hebben gedraaid.'
    above_target_template = 'Alle ARTs hebben de afgelopen %(target)d dagen ' \
        'succesvol gedraaid in de "%(street)s"-straat.'
    below_target_template = '%(value)d ARTs hebben de ' \
        'afgelopen %(target)d dagen niet succesvol gedraaid in de ' \
        '"%(street)s"-straat.'
    target_value = 3
    low_target_value = 7
    quality_attribute = TEST_QUALITY

    def value(self, days=0):  # pylint: disable=W0221
        return len(self._jenkins.unstable_arts_url(self.__street_regexp(), 
                                                   days=days or self.target()))

    def numerical_value(self):
        return self.value(days=self.target())

    def _is_below_target(self):
        return self.value(days=self.target()) > 0

    def _needs_immediate_action(self):
        return self.value(days=self.low_target()) > 0

    def _is_perfect(self):
        return self.value(days=1) == 0

    def _get_template(self):
        return self.below_target_template if self.value() > 0 \
            else self.above_target_template

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(ARTStability, self)._parameters()
        parameters['street'] = self.__street_name()
        return parameters

    def url(self):
        urls = dict()
        urls.update(self._jenkins.unstable_arts_url(self.__street_regexp(), 
                                                    days=self.target()))
        street_url = self._subject.url()
        if street_url:
            urls['"%s"-straat' % self.__street_name()] = street_url
        return urls

    def __street_name(self):
        ''' Return the name of the street. '''
        return self._subject.name()

    def __street_regexp(self):
        ''' Return the regular expression for the ARTs in the street. '''
        return self._subject.regexp()


class FailingCIJobs(JenkinsMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that fail. '''

    norm_template = 'Maximaal %(target)d van de CI-jobs%(responsible_team)s ' \
        'faalt. Meer dan %(low_target)d is rood. Een CI-job faalt als de ' \
        'laatste bouwpoging niet is geslaagd en er de afgelopen 24 uur geen ' \
        'geslaagde bouwpogingen zijn geweest.'
    template = '%(value)d van de %(number_of_jobs)d ' \
        'CI-jobs%(responsible_team)s faalt.'
    target_value = 0
    low_target_value = 2
    quality_attribute = ENVIRONMENT_QUALITY

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(FailingCIJobs, self)._parameters()
        parameters['responsible_team'] = self._responsible_team_text()
        parameters['number_of_jobs'] = self.__number_of_jobs()
        return parameters

    def value(self):
        return len(self._jenkins.failing_jobs_url(*self._teams()))

    def url(self):
        return self._jenkins.failing_jobs_url(*self._teams())

    def url_label(self):
        return 'Falende jobs'

    def __number_of_jobs(self):
        ''' Return the total number of jobs that the teams are responsible
            for. '''
        return self._jenkins.number_of_jobs(*self._teams())

    def _teams(self):
        ''' Return the teams to pass to Jenkins. '''
        raise NotImplementedError  # pragma: no cover

    def _responsible_team_text(self):
        ''' Return a text fragment to describe which team is responsible. '''
        raise NotImplementedError  # pragma: no cover


class TeamFailingCIJobs(FailingCIJobs):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that fail that a specific team is responsible for. '''

    name = 'Falende CI-jobs van een team'

    @classmethod
    def can_be_measured(cls, team, project):
        return super(TeamFailingCIJobs, cls).can_be_measured(team, project) \
            and len(project.teams()) > 1

    @classmethod
    def norm_template_default_values(cls):
        values = super(TeamFailingCIJobs, cls).norm_template_default_values()
        values['responsible_team'] = ' waarvoor een specifiek team ' \
            'verantwoordelijk is'
        return values

    def _teams(self):
        return (self._subject,)

    def _responsible_team_text(self):
        return ' waarvoor team %s verantwoordelijk is' % self._subject


class ProjectFailingCIJobs(FailingCIJobs):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs in a
        project that fail. '''

    name = 'Falende CI-jobs'

    @classmethod
    def norm_template_default_values(cls):
        values = super(ProjectFailingCIJobs, cls).norm_template_default_values()
        values['responsible_team'] = ''
        return values

    def _teams(self):
        return self.responsible_teams()

    def _responsible_team_text(self):
        return ''


class UnusedCIJobs(JenkinsMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that are not used. '''

    norm_template = 'Maximaal %(target)d van de CI-jobs%(responsible_team)s ' \
        'is ongebruikt. Meer dan %(low_target)d is rood. Een CI-job is ' \
        'ongebruikt als er de afgelopen 6 maanden geen bouwpogingen zijn ' \
        'geweest.'
    template = '%(value)d van de %(number_of_jobs)d ' \
        'CI-jobs%(responsible_team)s is ongebruikt.'
    target_value = 0
    low_target_value = 2
    quality_attribute = ENVIRONMENT_QUALITY

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(UnusedCIJobs, self)._parameters()
        parameters['responsible_team'] = self._responsible_team_text()
        parameters['number_of_jobs'] = self.__number_of_jobs()
        return parameters

    def value(self):
        return len(self._jenkins.unused_jobs_url(*self.__teams()))

    def url(self):
        return self._jenkins.unused_jobs_url(*self.__teams())

    def url_label(self):
        return 'Ongebruikte jobs'

    def _responsible_team_text(self):
        ''' Return a text fragment to describe which team is responsible. '''
        raise NotImplementedError  # pragma: no cover

    def __number_of_jobs(self):
        ''' Return the total number of jobs that the teams are responsible
            for. '''
        return self._jenkins.number_of_jobs(*self.__teams())

    def __teams(self):
        ''' Return the teams to pass to Jenkins. '''
        return (self._subject,) if self._subject else self.responsible_teams()


class ProjectUnusedCIJobs(UnusedCIJobs):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that are not used. '''

    name = 'Ongebruikte CI-jobs'

    @classmethod
    def norm_template_default_values(cls):
        values = super(ProjectUnusedCIJobs, cls).norm_template_default_values()
        values['responsible_team'] = ''
        return values

    def _responsible_team_text(self):
        return ''


class TeamUnusedCIJobs(UnusedCIJobs):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of continuous integration jobs
        that are not used and for which a specific team is responsible. '''

    name = 'Ongebruikte CI-jobs van een team'

    @classmethod
    def can_be_measured(cls, subject, project):
        return super(TeamUnusedCIJobs, cls).can_be_measured(subject, project) \
            and len(project.teams()) > 1

    @classmethod
    def norm_template_default_values(cls):
        values = super(TeamUnusedCIJobs, cls).norm_template_default_values()
        values['responsible_team'] = ' waarvoor een specifiek team ' \
            'verantwoordelijk is'
        return values

    def _responsible_team_text(self):
        return ' waarvoor team %s verantwoordelijk is' % self._subject 


class AssignedCIJobs(JenkinsMetricMixin, HigherPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of continuous integration jobs
        that is assigned to a team. Assign a job to a team by putting 
        "[RESPONSIBLE=<team name>]" in the description of the job. '''

    name = 'Toegewezen CI-jobs'
    norm_template = 'Minimaal %(target)d%% van de CI-jobs is toegewezen aan ' \
        'een team. Minder dan %(low_target)d%% is rood. Wijs een CI-job toe ' \
        'aan een team door "[RESPONSIBLE=teamnaam]" in de beschrijving ' \
        'van een CI-job op te nemen.'
    template = '%(value)d%% (%(numerator)d van %(denominator)d) van de ' \
        'CI-jobs is toegewezen aan een team.'
    target_value = 95
    low_target_value = 90
    quality_attribute = ENVIRONMENT_QUALITY

    @classmethod
    def can_be_measured(cls, subject, project):
        return super(AssignedCIJobs, cls).can_be_measured(subject, project) \
            and len(project.teams()) > 1

    def _numerator(self):
        return self._jenkins.number_of_assigned_jobs()

    def _denominator(self):
        return self._jenkins.number_of_jobs()

    def url(self):
        return self._jenkins.unassigned_jobs_url()

    def url_label(self):
        return 'Niet toegewezen jobs'
