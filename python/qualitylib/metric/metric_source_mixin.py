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

from qualitylib import metric_source, metric_info

# pylint: disable=R0903


class SonarMetricMixin(object):
    ''' Mixin class for metrics that use Sonar. '''
    metric_source_classes = (metric_source.Sonar,)

    def __init__(self, *args, **kwargs):
        super(SonarMetricMixin, self).__init__(*args, **kwargs)
        self._sonar = self._project.metric_source(metric_source.Sonar)
        self.__sonar_product_info = metric_info.SonarProductInfo(self._sonar,
                                                                 self._subject)

    @classmethod
    def can_be_measured(cls, product, project):
        ''' Return whether the metric can be measured. The metric can be
            measured when the project has Sonar and the product has a Sonar 
            id. '''
        sonar = project.metric_source(metric_source.Sonar)
        return super(SonarMetricMixin, cls).can_be_measured(product, project) \
            and cls.product_has_sonar_id(sonar, product)

    @staticmethod
    def product_has_sonar_id(sonar, product):
        ''' Return whether the product has a Sonar id. Can be overridden to 
            for example check a subcomponent for a Sonar id. '''
        product_sonar_info = metric_info.SonarProductInfo(sonar, product)
        return product_sonar_info.sonar_id()

    def url(self):
        ''' Return the url to Sonar. '''
        return dict(Sonar=self._sonar_url())

    def _sonar_url(self):
        ''' Return the Sonar url to use for the metric url. '''
        return self._sonar.url()

    def _sonar_id(self):
        ''' Return the id of the subject in Sonar. '''
        return self.__sonar_product_info.sonar_id()


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

    metric_source_classes = (metric_source.Jenkins,)

    def __init__(self, *args, **kwargs):
        super(JenkinsMetricMixin, self).__init__(*args, **kwargs)
        self._jenkins = self._project.metric_source(metric_source.Jenkins)


class BirtMetricMixin(object):
    ''' Mixin class for metrics that use Birt. '''

    metric_source_classes = (metric_source.Birt,)

    def __init__(self, *args, **kwargs):
        super(BirtMetricMixin, self).__init__(*args, **kwargs)
        self._birt = self._project.metric_source(metric_source.Birt)

    def _birt_id(self):
        ''' Return the id of the subject in Birt. '''
        return self._subject.metric_source_id(self._birt)


class BirtTestDesignMetricMixin(BirtMetricMixin):
    ''' Mixin class for metrics that use the Birt test design report. '''

    @classmethod
    def can_be_measured(cls, product, project):
        birt = project.metric_source(metric_source.Birt)
        return super(BirtTestDesignMetricMixin, cls).can_be_measured(product, 
                                                                     project) \
            and birt.has_test_design(product.metric_source_id(birt))

    def url(self):
        ''' Return the url for the What's Missing report instead of the 
            Birt test design report since the What's Missing report allows
            users to click to the user stories and test cases in Jira. '''
        return dict(Birt=self._birt.whats_missing_url(self._birt_id()))


class TrelloActionsBoardMetricMixin(object):
    ''' Mixin class for metrics that use Trello for an actions board. '''

    metric_source_classes = (metric_source.TrelloActionsBoard,)

    def __init__(self, *args, **kwargs):
        super(TrelloActionsBoardMetricMixin, self).__init__(*args, **kwargs)
        self._trello_actions_board = \
            self._project.metric_source(metric_source.TrelloActionsBoard)


class JiraMetricMixin(object):
    ''' Mixin class for metrics that use Jira. '''

    metric_source_classes = (metric_source.Jira,)

    def __init__(self, *args, **kwargs):
        super(JiraMetricMixin, self).__init__(*args, **kwargs)
        self._jira = self._project.metric_source(metric_source.Jira)


class SubversionMetricMixin(object):
    ''' Mixin class for metrics that use Subversion. '''

    metric_source_classes = (metric_source.Subversion,)

    def __init__(self, *args, **kwargs):
        super(SubversionMetricMixin, self).__init__(*args, **kwargs)
        self._subversion = self._project.metric_source(metric_source.Subversion)
        self.__subversion_product_info = metric_info.SubversionProductInfo( \
            self._subversion, self._subject)

    @classmethod
    def can_be_measured(cls, product, project):
        ''' Return whether the metric can be measured. The metric can be
            measured when the project has Subversion and the product has a
            Subversion path. '''
        subversion = project.metric_source(metric_source.Subversion)
        subversion_product_info = metric_info.SubversionProductInfo(subversion,
                                                                    product)
        return super(SubversionMetricMixin, cls).can_be_measured(product, 
                                                                 project) and \
            subversion and subversion_product_info.svn_path()

    def _svn_path(self):
        ''' Return the Subversion path for the product. '''
        return self.__subversion_product_info.svn_path()
