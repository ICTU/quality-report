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
from __future__ import absolute_import

import logging

from .. import metric_source, metric_info


class SonarMetricMixin(object):
    """ Mixin class for metrics that use Sonar. """
    metric_source_classes = (metric_source.Sonar,)

    def __init__(self, *args, **kwargs):
        super(SonarMetricMixin, self).__init__(*args, **kwargs)
        self._sonar = self._project.metric_source(metric_source.Sonar)
        self.__sonar_product_info = metric_info.SonarProductInfo(self._sonar, self._subject)

    def url(self):
        """ Return the url to Sonar. """
        url = self._sonar_url()
        return {} if url is None else dict(Sonar=self._sonar_url())

    def _sonar_url(self):
        """ Return the Sonar url to use for the metric url. """
        return self._sonar.url()

    def _sonar_id(self):
        """ Return the id of the subject in Sonar. """
        return self.__sonar_product_info.sonar_id()


class SonarDashboardMetricMixin(SonarMetricMixin):
    """ Mixin class for metrics that use the Sonar dashboard. """
    def _sonar_url(self):
        """ Return the url to the Sonar dashboard. """
        return self._sonar.dashboard_url(self._sonar_id())


class SonarViolationsMetricMixin(SonarMetricMixin):
    """ Mixin class for metrics that use the Sonar violations. """
    def _sonar_url(self):
        """ Return the url to the Sonar violations. """
        return self._sonar.violations_url(self._sonar_id())


class JenkinsMetricMixin(object):
    """ Mixin class for metrics that use Jenkins. """
    # pylint: disable=too-few-public-methods

    metric_source_classes = (metric_source.Jenkins,)

    def __init__(self, *args, **kwargs):
        super(JenkinsMetricMixin, self).__init__(*args, **kwargs)
        self._jenkins = self._project.metric_source(metric_source.Jenkins)


class BirtMetricMixin(object):  # pylint: disable=too-few-public-methods
    """ Mixin class for metrics that use Birt. """

    metric_source_classes = (metric_source.Birt,)

    def __init__(self, *args, **kwargs):
        super(BirtMetricMixin, self).__init__(*args, **kwargs)
        birt = self._project.metric_source(metric_source.Birt)
        if isinstance(birt, list):
            for birt_instance in birt:
                if self._subject.metric_source_id(birt_instance):
                    self._birt = birt_instance
                    break
            else:
                logging.warn("Couldn't find Birt instance for %s.", self._subject)
                self._birt = None
        else:
            self._birt = birt

    def _birt_id(self):
        """ Return the id of the subject in Birt. """
        return self._subject.metric_source_id(self._birt)


class BirtTestDesignMetricMixin(BirtMetricMixin):
    """ Mixin class for metrics that use the Birt test design report. """
    # pylint: disable=too-few-public-methods

    def url(self):
        """ Return the url for the What's Missing report instead of the Birt test design report since the
            What's Missing report allows users to click to the user stories and test cases in Jira. """
        url = self._birt.whats_missing_url(self._birt_id())
        return dict() if url is None else dict(Birt=url)


class TrelloActionsBoardMetricMixin(object):
    """ Mixin class for metrics that use Trello for an actions board. """
    # pylint: disable=too-few-public-methods

    metric_source_classes = (metric_source.TrelloActionsBoard,)

    def __init__(self, *args, **kwargs):
        super(TrelloActionsBoardMetricMixin, self).__init__(*args, **kwargs)
        self._trello_actions_board = self._project.metric_source(metric_source.TrelloActionsBoard)


class JiraMetricMixin(object):
    """ Mixin class for metrics that use Jira. """
    # pylint: disable=too-few-public-methods

    metric_source_classes = (metric_source.Jira,)

    def __init__(self, *args, **kwargs):
        super(JiraMetricMixin, self).__init__(*args, **kwargs)
        self._jira = self._project.metric_source(metric_source.Jira)


class VersionControlSystemMetricMixin(object):  # pylint: disable=too-few-public-methods
    """ Mixin class for metrics that use a version control system. """

    metric_source_classes = (metric_source.VersionControlSystem,)

    def __init__(self, *args, **kwargs):
        super(VersionControlSystemMetricMixin, self).__init__(*args, **kwargs)
        self.__vcs = self._project.metric_source(metric_source.VersionControlSystem)
        self._vcs_product_info = metric_info.VersionControlSystemProductInfo(self.__vcs, self._subject)

    def _vcs_path(self):
        """ Return the version control system path for the product. """
        return self._vcs_product_info.vcs_path()
